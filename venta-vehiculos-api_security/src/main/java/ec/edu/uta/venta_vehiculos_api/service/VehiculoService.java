package ec.edu.uta.venta_vehiculos_api.service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.Year;
import java.util.*;

import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import ec.edu.uta.venta_vehiculos_api.dto.*;
import ec.edu.uta.venta_vehiculos_api.exception.ApiError;
import ec.edu.uta.venta_vehiculos_api.model.HistorialPrecio;
import ec.edu.uta.venta_vehiculos_api.model.Vehiculo;
import ec.edu.uta.venta_vehiculos_api.repository.*;

@Service
@Transactional
public class VehiculoService {

    private final VehiculoRepository repo;
    private final ReservaRepository reservas;
    private final HistorialPrecioRepository historialRepo;

    public VehiculoService(
            VehiculoRepository repo,
            ReservaRepository reservas,
            HistorialPrecioRepository historialRepo) {
        this.repo = repo;
        this.reservas = reservas;
        this.historialRepo = historialRepo;
    }

    // F05: Filtrar vehículos por marca y disponibilidad
    @Transactional(readOnly = true)
    public List<VehiculoResponse> listar(String marca, String estado) {
        String estadoLimpio = null;
        if (estado != null && !estado.trim().isEmpty()) {
            estadoLimpio = estado.trim().toUpperCase(Locale.ROOT);
            if (!Set.of("DISPONIBLE", "RESERVADO", "VENDIDO").contains(estadoLimpio)) {
                throw new ApiError(400, "ESTADO_INVALIDO",
                        "Estado no válido. Permitidos: DISPONIBLE, RESERVADO, VENDIDO");
            }
        }

        List<Vehiculo> lista;
        boolean tieneMarca = (marca != null && !marca.trim().isEmpty());
        boolean tieneEstado = (estadoLimpio != null);

        if (tieneMarca && tieneEstado) {
            lista = repo.findByMarcaContainingIgnoreCaseAndEstado(marca.trim(), estadoLimpio);
        } else if (tieneMarca) {
            lista = repo.findByMarcaContainingIgnoreCase(marca.trim());
        } else if (tieneEstado) {
            lista = repo.findByEstado(estadoLimpio);
        } else {
            lista = repo.findAll();
        }

        return lista.stream()
                .map(VehiculoResponse::de)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<VehiculoResponse> listar(String marca) {
        return listar(marca, null);
    }

    @Transactional(readOnly = true)
    public VehiculoResponse obtener(int id) {
        return VehiculoResponse.de(
                repo.findById(id).orElseThrow(() -> falta()));
    }

    public VehiculoResponse crear(VehiculoRequest d) {
        Vehiculo v = new Vehiculo();
        copiar(v, d);
        v.setEstado("DISPONIBLE");
        return VehiculoResponse.de(repo.saveAndFlush(v));
    }

    // S11: Auditar cambios efectivos de precio en PUT
    public VehiculoResponse actualizar(int id, VehiculoRequest d) {
        Vehiculo v = editable(id);
        BigDecimal anterior = v.getPrecio();
        BigDecimal nuevo = d.precio();

        copiar(v, d);
        var guardado = repo.saveAndFlush(v);

        if (anterior != null && nuevo != null && anterior.compareTo(nuevo) != 0) {
            historialRepo.save(new HistorialPrecio(
                    guardado, anterior, nuevo, obtenerUsuarioActual(), LocalDateTime.now()));
        }

        return VehiculoResponse.de(guardado);
    }

    // S11: Auditar cambios efectivos de precio en PATCH
    public VehiculoResponse precio(int id, Map<String, Object> d) {
        if (d.size() != 1 || !d.containsKey("precio") || !(d.get("precio") instanceof Number)) {
            throw new ApiError(422, "PATCH_INVALIDO", "PATCH admite únicamente precio numérico y no nulo");
        }

        BigDecimal precio;
        try {
            precio = new BigDecimal(d.get("precio").toString());
        } catch (NumberFormatException e) {
            throw new ApiError(422, "PRECIO_INVALIDO", "Precio inválido");
        }

        if (precio.signum() <= 0 || precio.scale() > 2 || precio.compareTo(new BigDecimal("9999999999.99")) > 0) {
            throw new ApiError(422, "PRECIO_INVALIDO", "Precio positivo con máximo dos decimales");
        }

        Vehiculo v = editable(id);
        BigDecimal anterior = v.getPrecio();

        v.setPrecio(precio);
        var guardado = repo.saveAndFlush(v);

        if (anterior != null && anterior.compareTo(precio) != 0) {
            historialRepo.save(new HistorialPrecio(
                    guardado, anterior, precio, obtenerUsuarioActual(), LocalDateTime.now()));
        }

        return VehiculoResponse.de(guardado);
    }

    // S11: Consulta de historial de precios
    @Transactional(readOnly = true)
    public List<HistorialPrecioResponse> historialPrecios(int id) {
        if (!repo.existsById(id)) {
            throw falta();
        }
        return historialRepo.findByVehiculoIdVehiculoOrderByFechaDesc(id)
                .stream()
                .map(HistorialPrecioResponse::de)
                .toList();
    }

    public void eliminar(int id) {
        Vehiculo v = editable(id);
        if (reservas.existsByVehiculo_IdVehiculo(id)) {
            throw new ApiError(409, "HISTORIAL_RESERVAS", "Se conserva el vehículo por su historial de reservas");
        }
        repo.delete(v);
        repo.flush();
    }

    private Vehiculo editable(int id) {
        Vehiculo v = repo.bloquear(id).orElseThrow(() -> falta());
        if (!"DISPONIBLE".equals(v.getEstado())) {
            throw new ApiError(409, "VEHICULO_NO_DISPONIBLE",
                    "Un vehículo reservado o vendido no se modifica ni elimina");
        }
        return v;
    }

    private ApiError falta() {
        return new ApiError(404, "VEHICULO_NO_ENCONTRADO", "El vehículo no existe");
    }

    private String obtenerUsuarioActual() {
        var auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.getName() != null && !auth.getName().isBlank()) {
            return auth.getName();
        }
        return "sistema";
    }

    private void copiar(Vehiculo v, VehiculoRequest d) {
        if (d.anio() < 1900 || d.anio() > Year.now().getValue() + 1) {
            throw new ApiError(422, "ANIO_INVALIDO", "Año fuera de rango");
        }

        String placa = d.placa().toUpperCase(Locale.ROOT);
        String chasis = d.chasis().toUpperCase(Locale.ROOT);

        repo.findByPlaca(placa).ifPresent(x -> {
            if (v.getIdVehiculo() == null || !v.getIdVehiculo().equals(x.getIdVehiculo())) {
                throw new ApiError(409, "PLACA_DUPLICADA", "La placa ya pertenece a otro vehículo");
            }
        });

        repo.findByChasis(chasis).ifPresent(x -> {
            if (v.getIdVehiculo() == null || !v.getIdVehiculo().equals(x.getIdVehiculo())) {
                throw new ApiError(409, "CHASIS_DUPLICADO", "El chasis ya pertenece a otro vehículo");
            }
        });

        v.setPlaca(placa);
        v.setMarca(d.marca().trim());
        v.setModelo(d.modelo().trim());
        v.setAnio(d.anio());
        v.setChasis(chasis);
        v.setColor(d.color() != null && !d.color().trim().isEmpty() ? d.color().trim() : null);
        v.setPrecio(d.precio());
    }
}

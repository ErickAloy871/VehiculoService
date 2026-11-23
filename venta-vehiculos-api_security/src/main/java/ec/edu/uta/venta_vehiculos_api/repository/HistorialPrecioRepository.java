package ec.edu.uta.venta_vehiculos_api.repository;

import ec.edu.uta.venta_vehiculos_api.model.HistorialPrecio;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface HistorialPrecioRepository extends JpaRepository<HistorialPrecio, Integer> {
    List<HistorialPrecio> findByVehiculoIdVehiculoOrderByFechaDesc(Integer vehiculoId);
}


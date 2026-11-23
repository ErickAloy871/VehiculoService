package ec.edu.com;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.beans.property.ReadOnlyObjectWrapper;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.PasswordField;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Priority;
import javafx.scene.layout.Region;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

import java.util.List;
import java.util.concurrent.CompletionException;
import java.util.function.Function;

//venta equivalente a FormaPrincipal de windows forms 

public final class VehiculosApp extends Application {

    private final VehiculosApiClient api = new VehiculosApiClient();
    private final PasswordField txtToken = new PasswordField();
    private final Button btnConsultar = new Button("Consultar");
    private final Label lblEstado = new Label("Listo");
    private final Label lblTotal = new Label("Total de vehículos: 0");
    private final TableView<Vehiculo> tabla = new TableView<>();

    @Override
    public void start(Stage ventana) {
        Label titulo = new Label("Consulta de Vehículos Registrados");
        titulo.setStyle("-fx-font-size: 18px; -fx-font-weight: bold;");

        txtToken.setPromptText("Pega aquí el token JWT");
        txtToken.setMaxWidth(Double.MAX_VALUE);
        txtToken.setOnAction(e -> consultar());
        HBox.setHgrow(txtToken, Priority.ALWAYS);

        btnConsultar.setDefaultButton(true);
        btnConsultar.setOnAction(e -> consultar());

        HBox barraConsulta = new HBox(10, txtToken, btnConsultar);
        barraConsulta.setAlignment(Pos.CENTER_LEFT);

        configurarTabla();
        VBox.setVgrow(tabla, Priority.ALWAYS);

        Region espaciador = new Region();
        HBox.setHgrow(espaciador, Priority.ALWAYS);
        HBox barraEstado = new HBox(10, lblEstado, espaciador, lblTotal);
        barraEstado.setAlignment(Pos.CENTER_LEFT);

        VBox contenido = new VBox(12, titulo, barraConsulta, tabla, barraEstado);
        contenido.setPadding(new Insets(22));
        contenido.setStyle("-fx-background-color: white;");

        ventana.setScene(new Scene(contenido, 1024, 650));
        ventana.setTitle("Consulta de Vehículos");
        ventana.show();
    }

    private void configurarTabla() {
        tabla.setPlaceholder(new Label("Ingresa tu token JWT y presiona Consultar."));
        tabla.setColumnResizePolicy(TableView.CONSTRAINED_RESIZE_POLICY);

        tabla.getColumns().addAll(List.of(
                crearColumna("ID", Vehiculo::idVehiculo),
                crearColumna("Marca", Vehiculo::marca),
                crearColumna("Modelo", Vehiculo::modelo),
                crearColumna("Placa", Vehiculo::placa),
                crearColumna("Chasis", Vehiculo::chasis),
                crearColumna("Año", Vehiculo::anio),
                crearColumna("Color", Vehiculo::color),
                crearColumna("Precio", Vehiculo::precio),
                crearColumna("Estado", Vehiculo::estado)
        ));
    }

    private <T> TableColumn<Vehiculo, T> crearColumna(String titulo, Function<Vehiculo, T> extractor) {
        TableColumn<Vehiculo, T> columna = new TableColumn<>(titulo);
        columna.setCellValueFactory(dato -> new ReadOnlyObjectWrapper<>(extractor.apply(dato.getValue())));
        return columna;
    }

    private void consultar() {
        String token = txtToken.getText() == null ? "" : txtToken.getText().trim();
        if (token.isEmpty()) {
            mostrarEstado("Ingresa el token JWT antes de consultar.", "#c62828");
            txtToken.requestFocus();
            return;
        }

        btnConsultar.setDisable(true);
        mostrarEstado("Consultando vehículos en la API...", "#1565c0");

        api.consultarVehiculos(token).whenComplete((resultado, error) -> Platform.runLater(() -> {
            btnConsultar.setDisable(false);

            if (error != null) {
                Throwable causa = error instanceof CompletionException && error.getCause() != null
                        ? error.getCause()
                        : error;
                String detalle = (causa.getMessage() != null && !causa.getMessage().isBlank())
                        ? causa.getMessage()
                        : causa.getClass().getSimpleName()
                                + " (verifica que la API esté ejecutándose en http://127.0.0.1:8080)";
                mostrarEstado("Error de conexión o lectura: " + detalle, "#c62828");
                return;
            }

            int codigo = resultado.codigoHttp();
            if (codigo == 200) {
                List<Vehiculo> vehiculos = resultado.vehiculos();
                tabla.getItems().setAll(vehiculos);
                lblTotal.setText("Total de vehículos: " + vehiculos.size());
                mostrarEstado("Consulta exitosa (HTTP 200).", "#2e7d32");
                return;
            }

            tabla.getItems().clear();
            lblTotal.setText("Total de vehículos: 0");
            String mensaje = switch (codigo) {
                case 401 -> "No autenticado (HTTP 401): token inválido o expirado.";
                case 403 -> "Sin permiso (HTTP 403): el rol del token no puede consultar vehículos.";
                default -> "Error HTTP " + codigo + " al consultar la API.";
            };
            mostrarEstado(mensaje, "#c62828");
        }));
    }
 
    private void mostrarEstado(String mensaje, String colorHex) {
        lblEstado.setText(mensaje);
        lblEstado.setStyle("-fx-text-fill: " + colorHex + ";");
    }
}

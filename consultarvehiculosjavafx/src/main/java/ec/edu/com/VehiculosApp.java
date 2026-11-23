package ec.edu.com;

import javafx.animation.Animation;
import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.beans.property.ReadOnlyObjectWrapper;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Priority;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;
import javafx.util.Duration;

import java.util.List;

public final class VehiculosApp extends Application {

    private final NotificacionesApiClient api = new NotificacionesApiClient();
    private final Button btnRefrescar = new Button("Actualizar Ahora");
    private final Label lblEstadoConexion = new Label("🟢 Conectado · Sondeo activo cada 3s");
    private final Label lblTotal = new Label("Total de notificaciones: 0");
    private final TableView<Notificacion> tabla = new TableView<>();
    private Timeline timeline;

    @Override
    public void start(Stage ventana) {
        ventana.setTitle("Sistema de Notificaciones de Ventas · JavaFX");

        Label titulo = new Label("Monitor de Avisos y Notificaciones de Venta");
        titulo.setStyle("-fx-font-size: 18px; -fx-font-weight: bold; -fx-text-fill: #103b56;");

        Label subtitulo = new Label("Eventos procesados desde RabbitMQ (notificaciones.ventas) vía NGINX (:8090)");
        subtitulo.setStyle("-fx-font-size: 12px; -fx-text-fill: #5a7382;");

        configurarTabla();

        btnRefrescar.setStyle(
                "-fx-background-color: #10597b; -fx-text-fill: white; -fx-font-weight: bold; -fx-padding: 6 14;");
        btnRefrescar.setOnAction(e -> consultarNotificaciones());

        lblEstadoConexion.setStyle("-fx-font-size: 12px; -fx-font-weight: bold; -fx-text-fill: #157344;");
        lblTotal.setStyle("-fx-font-size: 12px; -fx-font-weight: bold; -fx-text-fill: #22516b;");

        HBox barraAcciones = new HBox(12, btnRefrescar, lblEstadoConexion, lblTotal);
        barraAcciones.setAlignment(Pos.CENTER_LEFT);

        VBox raiz = new VBox(14, titulo, subtitulo, barraAcciones, tabla);
        raiz.setPadding(new Insets(18));
        VBox.setVgrow(tabla, Priority.ALWAYS);

        Scene escena = new Scene(raiz, 820, 520);
        ventana.setScene(escena);
        ventana.show();

        // 1. Consulta inicial inmediata
        consultarNotificaciones();

        // 2. Sondeo automático cada 3 segundos (según Actividad 9)
        timeline = new Timeline(new KeyFrame(Duration.seconds(3), e -> consultarNotificaciones()));
        timeline.setCycleCount(Animation.INDEFINITE);
        timeline.play();
    }

    private void configurarTabla() {
        tabla.setPlaceholder(new Label("No hay notificaciones recibidas todavía."));

        TableColumn<Notificacion, Long> colId = new TableColumn<>("ID");
        colId.setCellValueFactory(c -> new ReadOnlyObjectWrapper<>(c.getValue().id()));
        colId.setPrefWidth(60);

        TableColumn<Notificacion, String> colTipo = new TableColumn<>("Tipo");
        colTipo.setCellValueFactory(c -> new ReadOnlyObjectWrapper<>(c.getValue().tipo()));
        colTipo.setPrefWidth(90);

        TableColumn<Notificacion, Integer> colVenta = new TableColumn<>("Venta ID");
        colVenta.setCellValueFactory(c -> new ReadOnlyObjectWrapper<>(c.getValue().ventaId()));
        colVenta.setPrefWidth(85);

        TableColumn<Notificacion, Integer> colVehiculo = new TableColumn<>("Vehículo ID");
        colVehiculo.setCellValueFactory(c -> new ReadOnlyObjectWrapper<>(c.getValue().vehiculoId()));
        colVehiculo.setPrefWidth(95);

        TableColumn<Notificacion, String> colMensaje = new TableColumn<>("Mensaje de Evento");
        colMensaje.setCellValueFactory(c -> new ReadOnlyObjectWrapper<>(c.getValue().mensaje()));
        colMensaje.setPrefWidth(300);

        TableColumn<Notificacion, String> colFecha = new TableColumn<>("Fecha / Hora");
        colFecha.setCellValueFactory(c -> new ReadOnlyObjectWrapper<>(c.getValue().fechaHora()));
        colFecha.setPrefWidth(160);

        tabla.getColumns().addAll(colId, colTipo, colVenta, colVehiculo, colMensaje, colFecha);
    }

    private void consultarNotificaciones() {
        api.consultarNotificaciones().thenAccept(resultado -> Platform.runLater(() -> {
            if (resultado.error() != null) {
                lblEstadoConexion.setText("🔴 " + resultado.error());
                lblEstadoConexion.setStyle("-fx-font-size: 12px; -fx-font-weight: bold; -fx-text-fill: #9a2f2f;");
                return;
            }

            lblEstadoConexion.setText("🟢 Conectado · Sondeo activo cada 3s");
            lblEstadoConexion.setStyle("-fx-font-size: 12px; -fx-font-weight: bold; -fx-text-fill: #157344;");

            List<Notificacion> lista = resultado.notificaciones();
            lblTotal.setText("Total: " + lista.size() + " notificaciones");

            // Solo actualizar si hay cambios para no perder el foco o selección
            if (tabla.getItems().size() != lista.size()) {
                tabla.getItems().setAll(lista);
            }
        }));
    }

    @Override
    public void stop() {
        if (timeline != null) {
            timeline.stop();
        }
    }
}

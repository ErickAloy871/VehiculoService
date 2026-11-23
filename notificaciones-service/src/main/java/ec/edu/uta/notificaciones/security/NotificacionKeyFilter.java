package ec.edu.uta.notificaciones.security;


import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import jakarta.servlet.*;
import jakarta.servlet.http.*;


@Component 
public class NotificacionKeyFilter extends OncePerRequestFilter{
    private final String key;
    public NotificacionKeyFilter(@Value("${app.notificacion-key}") String key){
        if(key.length()<32) throw new IllegalArgumentException("Clave no cumple los 32 crt");
        this.key=key;
    }
    @Override
    protected void doFilterInternal(HttpServletRequest req,
    HttpServletResponse res, FilterChain chain)
    throws IOException, ServletException {
  
    // Permitir consultas GET (utilizadas por JavaFX) sin exponer clave interna
    if ("GET".equalsIgnoreCase(req.getMethod())) {
        chain.doFilter(req, res);
        return;
    }

    String h=req.getHeader("X-Notification-Key");
    if (h==null || !MessageDigest.isEqual(
        key.getBytes(StandardCharsets.UTF_8),
        h.getBytes(StandardCharsets.UTF_8))){
            res.setStatus(401);
            res.setContentType("application/problem+json");
            res.getWriter().write("{\"status\":401, \"title\":\"Clave no valida\"}");
            return;
        }
        chain.doFilter(req,res);
    }

} 
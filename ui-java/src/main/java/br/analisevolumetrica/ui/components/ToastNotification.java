package br.analisevolumetrica.ui.components;

import br.analisevolumetrica.ui.utils.DesignConstants;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

/**
 * Notificação Toast moderna e não-bloqueante
 * Aparece no canto superior direito e desaparece automaticamente
 *
 * @author Claude Code
 */
public class ToastNotification extends JWindow {

    public enum Type {
        SUCCESS(DesignConstants.SUCCESS, DesignConstants.ICON_SUCCESS),
        ERROR(DesignConstants.ERROR, DesignConstants.ICON_ERROR),
        WARNING(DesignConstants.WARNING, DesignConstants.ICON_WARNING),
        INFO(DesignConstants.INFO, DesignConstants.ICON_INFO);

        public final Color color;
        public final String icon;

        Type(Color color, String icon) {
            this.color = color;
            this.icon = icon;
        }
    }

    private static final int TOAST_WIDTH = 380;
    private static final int TOAST_HEIGHT = 90;
    private static final int ANIMATION_STEPS = 20;
    private static final int ANIMATION_DELAY = 15;
    private static final int DISPLAY_DURATION = 3000;

    private Timer animationTimer;
    private Timer displayTimer;
    private float opacity = 0.0f;
    private boolean fadingOut = false;

    /**
     * Cria e exibe uma notificação toast
     */
    public ToastNotification(JFrame parent, String title, String message, Type type) {
        super(parent);
        createUI(title, message, type);
        positionToast(parent);
        fadeIn();
    }

    /**
     * Método estático de conveniência para mostrar toast de sucesso
     */
    public static void showSuccess(JFrame parent, String title, String message) {
        new ToastNotification(parent, title, message, Type.SUCCESS);
    }

    /**
     * Método estático de conveniência para mostrar toast de erro
     */
    public static void showError(JFrame parent, String title, String message) {
        new ToastNotification(parent, title, message, Type.ERROR);
    }

    /**
     * Método estático de conveniência para mostrar toast de aviso
     */
    public static void showWarning(JFrame parent, String title, String message) {
        new ToastNotification(parent, title, message, Type.WARNING);
    }

    /**
     * Método estático de conveniência para mostrar toast de info
     */
    public static void showInfo(JFrame parent, String title, String message) {
        new ToastNotification(parent, title, message, Type.INFO);
    }

    private void createUI(String title, String message, Type type) {
        setSize(TOAST_WIDTH, TOAST_HEIGHT);
        setLayout(new BorderLayout());

        // Painel principal
        JPanel mainPanel = new JPanel(new BorderLayout(DesignConstants.SPACING_MEDIUM, DesignConstants.SPACING_SMALL));
        mainPanel.setBackground(Color.WHITE);
        mainPanel.setBorder(new EmptyBorder(
                DesignConstants.SPACING_MEDIUM,
                DesignConstants.SPACING_MEDIUM,
                DesignConstants.SPACING_MEDIUM,
                DesignConstants.SPACING_MEDIUM
        ));

        // Estilo com borda colorida à esquerda
        String style = String.format(
                "arc:%d;background:#FFFFFF;border:0,0,0,4,%s",
                DesignConstants.BORDER_RADIUS_SMALL,
                DesignConstants.toHex(type.color)
        );
        mainPanel.putClientProperty("FlatLaf.style", style);

        // Ícone
        JLabel iconLabel = new JLabel(type.icon);
        iconLabel.setFont(new Font("Segoe UI Emoji", Font.PLAIN, 32));
        iconLabel.setForeground(type.color);
        iconLabel.setBorder(new EmptyBorder(0, 0, 0, DesignConstants.SPACING_SMALL));

        // Painel de texto
        JPanel textPanel = new JPanel();
        textPanel.setLayout(new BoxLayout(textPanel, BoxLayout.Y_AXIS));
        textPanel.setOpaque(false);

        // Título
        JLabel titleLabel = new JLabel(title);
        titleLabel.setFont(DesignConstants.FONT_BODY_BOLD);
        titleLabel.setForeground(DesignConstants.TEXT_PRIMARY);
        titleLabel.setAlignmentX(Component.LEFT_ALIGNMENT);

        // Mensagem (pode ser HTML)
        JLabel messageLabel = new JLabel(
                "<html><div style='width: 250px;'>" + message + "</div></html>"
        );
        messageLabel.setFont(DesignConstants.FONT_SMALL);
        messageLabel.setForeground(DesignConstants.TEXT_SECONDARY);
        messageLabel.setAlignmentX(Component.LEFT_ALIGNMENT);

        textPanel.add(titleLabel);
        textPanel.add(Box.createVerticalStrut(DesignConstants.SPACING_TINY));
        textPanel.add(messageLabel);

        // Botão de fechar (X)
        JButton closeButton = new JButton("×");
        closeButton.setFont(new Font("Arial", Font.PLAIN, 20));
        closeButton.setForeground(DesignConstants.TEXT_SECONDARY);
        closeButton.setContentAreaFilled(false);
        closeButton.setBorderPainted(false);
        closeButton.setFocusPainted(false);
        closeButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        closeButton.setPreferredSize(new Dimension(30, 30));
        closeButton.addActionListener(e -> fadeOut());
        closeButton.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                closeButton.setForeground(DesignConstants.TEXT_PRIMARY);
            }

            @Override
            public void mouseExited(MouseEvent e) {
                closeButton.setForeground(DesignConstants.TEXT_SECONDARY);
            }
        });

        // Painel superior com texto e botão fechar
        JPanel topPanel = new JPanel(new BorderLayout());
        topPanel.setOpaque(false);
        topPanel.add(textPanel, BorderLayout.CENTER);
        topPanel.add(closeButton, BorderLayout.EAST);

        // Montar layout
        mainPanel.add(iconLabel, BorderLayout.WEST);
        mainPanel.add(topPanel, BorderLayout.CENTER);

        add(mainPanel);

        // Click em qualquer lugar fecha o toast
        mainPanel.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                fadeOut();
            }
        });
    }

    private void positionToast(JFrame parent) {
        // Posicionar no canto superior direito
        if (parent != null && parent.isVisible()) {
            Point parentLocation = parent.getLocationOnScreen();
            Dimension parentSize = parent.getSize();
            setLocation(
                    parentLocation.x + parentSize.width - TOAST_WIDTH - 20,
                    parentLocation.y + 80 // Abaixo do menu
            );
        } else {
            // Se não tiver parent, usar canto da tela
            Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
            setLocation(
                    screenSize.width - TOAST_WIDTH - 20,
                    100
            );
        }
    }

    private void fadeIn() {
        setOpacity(0.0f);
        setVisible(true);

        animationTimer = new Timer(ANIMATION_DELAY, e -> {
            opacity += 1.0f / ANIMATION_STEPS;
            if (opacity >= 0.98f) {
                opacity = 0.98f;
                animationTimer.stop();
                startDisplayTimer();
            }
            setOpacity(opacity);
        });
        animationTimer.start();
    }

    private void fadeOut() {
        if (fadingOut) return;
        fadingOut = true;

        if (displayTimer != null) {
            displayTimer.stop();
        }

        animationTimer = new Timer(ANIMATION_DELAY, e -> {
            opacity -= 1.0f / ANIMATION_STEPS;
            if (opacity <= 0.0f) {
                opacity = 0.0f;
                animationTimer.stop();
                dispose();
            }
            setOpacity(opacity);
        });
        animationTimer.start();
    }

    private void startDisplayTimer() {
        displayTimer = new Timer(DISPLAY_DURATION, e -> fadeOut());
        displayTimer.setRepeats(false);
        displayTimer.start();
    }

    /**
     * Exibe uma notificação com ação customizada
     */
    public static ToastNotification showWithAction(
            JFrame parent,
            String title,
            String message,
            Type type,
            String actionText,
            Runnable action) {

        ToastNotification toast = new ToastNotification(parent, title, message, type);

        // Adicionar botão de ação (se necessário no futuro)
        // TODO: Implementar botão de ação no toast

        return toast;
    }
}

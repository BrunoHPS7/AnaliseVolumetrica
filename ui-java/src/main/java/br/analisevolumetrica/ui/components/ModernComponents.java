package br.analisevolumetrica.ui.components;

import br.analisevolumetrica.ui.utils.DesignConstants;
import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

/**
 * Componentes modernos reutilizáveis para a interface
 * Cards, botões, labels com estilos consistentes
 *
 * @author Claude Code
 */
public class ModernComponents {

    /**
     * Cria um card moderno com título, descrição e ação
     */
    public static JPanel createActionCard(
            String emoji,
            String title,
            String description,
            String buttonText,
            Color accentColor,
            Runnable action) {

        JPanel card = new JPanel();
        card.setLayout(new BorderLayout(DesignConstants.SPACING_MEDIUM, DesignConstants.SPACING_MEDIUM));
        card.setBackground(DesignConstants.CARD_BG);
        card.setBorder(new EmptyBorder(
                DesignConstants.SPACING_LARGE,
                DesignConstants.SPACING_LARGE,
                DesignConstants.SPACING_LARGE,
                DesignConstants.SPACING_LARGE
        ));
        card.setPreferredSize(new Dimension(DesignConstants.CARD_MIN_WIDTH, DesignConstants.CARD_MIN_HEIGHT));

        // Estilo do card
        String cardStyle = String.format(
                "arc:%d;background:%s;border:1,1,1,1,%s",
                DesignConstants.BORDER_RADIUS_MEDIUM,
                DesignConstants.HEX_CARD_BG,
                DesignConstants.HEX_BORDER
        );
        card.putClientProperty("FlatLaf.style", cardStyle);

        // Ícone/Emoji no topo
        JLabel iconLabel = new JLabel(emoji, SwingConstants.CENTER);
        iconLabel.setFont(new Font("Segoe UI Emoji", Font.PLAIN, 48));
        iconLabel.setForeground(accentColor);

        // Título
        JLabel titleLabel = new JLabel(title, SwingConstants.CENTER);
        titleLabel.setFont(DesignConstants.FONT_HEADING);
        titleLabel.setForeground(DesignConstants.TEXT_PRIMARY);

        // Descrição
        JLabel descLabel = new JLabel(
                "<html><div style='text-align: center;'>" + description + "</div></html>",
                SwingConstants.CENTER
        );
        descLabel.setFont(DesignConstants.FONT_BODY);
        descLabel.setForeground(DesignConstants.TEXT_SECONDARY);

        // Painel central com ícone, título e descrição
        JPanel centerPanel = new JPanel();
        centerPanel.setLayout(new BoxLayout(centerPanel, BoxLayout.Y_AXIS));
        centerPanel.setBackground(DesignConstants.CARD_BG);
        centerPanel.setOpaque(false);

        iconLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        titleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        descLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        centerPanel.add(iconLabel);
        centerPanel.add(Box.createVerticalStrut(DesignConstants.SPACING_SMALL));
        centerPanel.add(titleLabel);
        centerPanel.add(Box.createVerticalStrut(DesignConstants.SPACING_TINY));
        centerPanel.add(descLabel);

        // Botão de ação
        JButton actionButton = createPrimaryButton(buttonText, accentColor);
        actionButton.addActionListener(e -> action.run());

        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER));
        buttonPanel.setOpaque(false);
        buttonPanel.add(actionButton);

        // Montar card
        card.add(centerPanel, BorderLayout.CENTER);
        card.add(buttonPanel, BorderLayout.SOUTH);

        // Efeito hover no card
        addCardHoverEffect(card, accentColor);

        return card;
    }

    /**
     * Cria um botão primário moderno
     */
    public static JButton createPrimaryButton(String text, Color bgColor) {
        JButton button = new JButton(text);
        button.setFont(DesignConstants.FONT_BODY_BOLD);
        button.setForeground(Color.WHITE);
        button.setBackground(bgColor);
        button.setFocusPainted(false);
        button.setBorderPainted(false);
        button.setCursor(new Cursor(Cursor.HAND_CURSOR));

        String hexColor = DesignConstants.toHex(bgColor);
        String styleNormal = String.format(
                "arc:%d;background:%s;foreground:#FFFFFF;borderWidth:0;focusWidth:0",
                DesignConstants.BORDER_RADIUS_SMALL,
                hexColor
        );

        String styleHover = String.format(
                "arc:%d;background:lighten(%s,5%%);foreground:#FFFFFF;borderWidth:0",
                DesignConstants.BORDER_RADIUS_SMALL,
                hexColor
        );

        String stylePressed = String.format(
                "arc:%d;background:darken(%s,10%%);foreground:#FFFFFF;borderWidth:0",
                DesignConstants.BORDER_RADIUS_SMALL,
                hexColor
        );

        button.putClientProperty("FlatLaf.style", styleNormal);

        button.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                button.putClientProperty("FlatLaf.style", styleHover);
            }

            @Override
            public void mouseExited(MouseEvent e) {
                button.putClientProperty("FlatLaf.style", styleNormal);
            }

            @Override
            public void mousePressed(MouseEvent e) {
                button.putClientProperty("FlatLaf.style", stylePressed);
            }

            @Override
            public void mouseReleased(MouseEvent e) {
                if (button.contains(e.getPoint())) {
                    button.putClientProperty("FlatLaf.style", styleHover);
                } else {
                    button.putClientProperty("FlatLaf.style", styleNormal);
                }
            }
        });

        return button;
    }

    /**
     * Cria um botão outline (borda, sem preenchimento)
     */
    public static JButton createOutlineButton(String text, Color borderColor) {
        JButton button = new JButton(text);
        button.setFont(DesignConstants.FONT_BODY_BOLD);
        button.setForeground(borderColor);
        button.setBackground(Color.WHITE);
        button.setFocusPainted(false);
        button.setCursor(new Cursor(Cursor.HAND_CURSOR));

        String hexColor = DesignConstants.toHex(borderColor);
        String styleNormal = String.format(
                "arc:%d;background:#FFFFFF;foreground:%s;borderWidth:2;borderColor:%s;focusWidth:0",
                DesignConstants.BORDER_RADIUS_SMALL,
                hexColor,
                hexColor
        );

        String styleHover = String.format(
                "arc:%d;background:%s;foreground:#FFFFFF;borderWidth:2;borderColor:%s",
                DesignConstants.BORDER_RADIUS_SMALL,
                hexColor,
                hexColor
        );

        button.putClientProperty("FlatLaf.style", styleNormal);

        button.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                button.putClientProperty("FlatLaf.style", styleHover);
            }

            @Override
            public void mouseExited(MouseEvent e) {
                button.putClientProperty("FlatLaf.style", styleNormal);
            }
        });

        return button;
    }

    /**
     * Adiciona efeito hover a um card
     */
    public static void addCardHoverEffect(JPanel card, Color accentColor) {
        String hexColor = DesignConstants.toHex(accentColor);

        String styleNormal = String.format(
                "arc:%d;background:%s;border:1,1,1,1,%s",
                DesignConstants.BORDER_RADIUS_MEDIUM,
                DesignConstants.HEX_CARD_BG,
                DesignConstants.HEX_BORDER
        );

        String styleHover = String.format(
                "arc:%d;background:lighten(@background,2%%);border:2,2,2,2,%s",
                DesignConstants.BORDER_RADIUS_MEDIUM,
                hexColor
        );

        card.setCursor(new Cursor(Cursor.HAND_CURSOR));

        card.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                card.putClientProperty("FlatLaf.style", styleHover);
            }

            @Override
            public void mouseExited(MouseEvent e) {
                card.putClientProperty("FlatLaf.style", styleNormal);
            }
        });
    }

    /**
     * Cria um indicador de status (conexão, etc.)
     */
    public static JPanel createStatusIndicator(String text, boolean isConnected) {
        JPanel panel = new JPanel(new FlowLayout(FlowLayout.LEFT, DesignConstants.SPACING_SMALL, 0));
        panel.setOpaque(false);

        // Indicador visual (bolinha)
        JLabel indicator = new JLabel(DesignConstants.ICON_CONNECTED);
        indicator.setFont(DesignConstants.FONT_SMALL);
        indicator.setForeground(isConnected ? DesignConstants.SUCCESS : DesignConstants.ERROR);

        // Texto do status
        JLabel statusLabel = new JLabel(text);
        statusLabel.setFont(DesignConstants.FONT_SMALL);
        statusLabel.setForeground(DesignConstants.TEXT_SECONDARY);

        panel.add(indicator);
        panel.add(statusLabel);

        return panel;
    }

    /**
     * Cria um título de seção
     */
    public static JLabel createSectionTitle(String text) {
        JLabel label = new JLabel(text, SwingConstants.CENTER);
        label.setFont(DesignConstants.FONT_TITLE);
        label.setForeground(DesignConstants.TEXT_PRIMARY);
        return label;
    }

    /**
     * Cria um subtítulo de seção
     */
    public static JLabel createSectionSubtitle(String text) {
        JLabel label = new JLabel(
                "<html><div style='text-align: center;'>" + text + "</div></html>",
                SwingConstants.CENTER
        );
        label.setFont(DesignConstants.FONT_BODY);
        label.setForeground(DesignConstants.TEXT_SECONDARY);
        return label;
    }

    /**
     * Cria um painel com grid de cards
     */
    public static JPanel createCardGrid(int columns) {
        JPanel panel = new JPanel(new GridLayout(0, columns, DesignConstants.SPACING_LARGE, DesignConstants.SPACING_LARGE));
        panel.setOpaque(false);
        panel.setBorder(new EmptyBorder(
                DesignConstants.SPACING_LARGE,
                DesignConstants.SPACING_XLARGE,
                DesignConstants.SPACING_LARGE,
                DesignConstants.SPACING_XLARGE
        ));
        return panel;
    }

    /**
     * Cria um separador visual
     */
    public static Component createVerticalSpacer(int height) {
        return Box.createVerticalStrut(height);
    }

    /**
     * Cria um separador horizontal
     */
    public static JSeparator createSeparator() {
        JSeparator separator = new JSeparator();
        separator.setForeground(DesignConstants.BORDER);
        separator.setBackground(DesignConstants.BORDER);
        return separator;
    }

    /**
     * Cria um card de passo do workflow (sequencial) - card inteiro clicável
     */
    public static JPanel createStepCard(
            int stepNumber,
            String emoji,
            String title,
            String description,
            String buttonText,
            Color accentColor,
            Runnable action) {

        JPanel card = new JPanel();
        card.setLayout(new BorderLayout(DesignConstants.SPACING_MEDIUM, DesignConstants.SPACING_MEDIUM));
        card.setBackground(DesignConstants.CARD_BG);
        card.setBorder(new EmptyBorder(
                DesignConstants.SPACING_LARGE,
                DesignConstants.SPACING_LARGE,
                DesignConstants.SPACING_LARGE,
                DesignConstants.SPACING_LARGE
        ));
        card.setMaximumSize(new Dimension(Integer.MAX_VALUE, 100));
        card.setPreferredSize(new Dimension(800, 100));

        // Estilo do card
        String cardStyle = String.format(
                "arc:%d;background:%s;border:2,2,2,2,%s",
                DesignConstants.BORDER_RADIUS_MEDIUM,
                DesignConstants.HEX_CARD_BG,
                DesignConstants.toHex(accentColor)
        );
        card.putClientProperty("FlatLaf.style", cardStyle);

        // Painel esquerdo: Número do passo + Emoji
        JPanel leftPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, DesignConstants.SPACING_MEDIUM, 0));
        leftPanel.setOpaque(false);

        // Número do passo em círculo
        JLabel stepLabel = new JLabel(String.valueOf(stepNumber), SwingConstants.CENTER);
        stepLabel.setFont(new Font("Segoe UI", Font.BOLD, 24));
        stepLabel.setForeground(Color.WHITE);
        stepLabel.setBackground(accentColor);
        stepLabel.setOpaque(true);
        stepLabel.setPreferredSize(new Dimension(50, 50));
        stepLabel.setBorder(new EmptyBorder(0, 0, 0, 0));

        String circleStyle = String.format(
                "arc:%d;background:%s",
                25, // metade de 50 para fazer círculo
                DesignConstants.toHex(accentColor)
        );
        stepLabel.putClientProperty("FlatLaf.style", circleStyle);

        // Emoji
        JLabel iconLabel = new JLabel(emoji);
        iconLabel.setFont(new Font("Segoe UI Emoji", Font.PLAIN, 32));

        leftPanel.add(stepLabel);
        leftPanel.add(Box.createHorizontalStrut(DesignConstants.SPACING_MEDIUM));
        leftPanel.add(iconLabel);

        // Painel central: Título e Descrição
        JPanel centerPanel = new JPanel();
        centerPanel.setLayout(new BoxLayout(centerPanel, BoxLayout.Y_AXIS));
        centerPanel.setOpaque(false);

        JLabel titleLabel = new JLabel(title);
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 18));
        titleLabel.setForeground(DesignConstants.TEXT_PRIMARY);
        titleLabel.setAlignmentX(Component.LEFT_ALIGNMENT);

        JLabel descLabel = new JLabel(description);
        descLabel.setFont(DesignConstants.FONT_BODY);
        descLabel.setForeground(DesignConstants.TEXT_SECONDARY);
        descLabel.setAlignmentX(Component.LEFT_ALIGNMENT);

        centerPanel.add(Box.createVerticalGlue());
        centerPanel.add(titleLabel);
        centerPanel.add(Box.createVerticalStrut(4));
        centerPanel.add(descLabel);
        centerPanel.add(Box.createVerticalGlue());

        // Painel direito: Seta indicadora
        JPanel rightPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        rightPanel.setOpaque(false);

        JLabel arrowLabel = new JLabel("→");
        arrowLabel.setFont(new Font("Segoe UI", Font.BOLD, 32));
        arrowLabel.setForeground(accentColor);
        rightPanel.add(arrowLabel);

        // Montar card
        card.add(leftPanel, BorderLayout.WEST);
        card.add(centerPanel, BorderLayout.CENTER);
        card.add(rightPanel, BorderLayout.EAST);

        // Card inteiro clicável
        card.setCursor(new Cursor(Cursor.HAND_CURSOR));

        // Efeito hover mais destacado
        String styleHover = String.format(
                "arc:%d;background:lighten(@background,4%%);border:3,3,3,3,%s",
                DesignConstants.BORDER_RADIUS_MEDIUM,
                DesignConstants.toHex(accentColor)
        );

        String stylePressed = String.format(
                "arc:%d;background:darken(@background,2%%);border:2,2,2,2,%s",
                DesignConstants.BORDER_RADIUS_MEDIUM,
                DesignConstants.toHex(accentColor)
        );

        card.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                card.putClientProperty("FlatLaf.style", styleHover);
                arrowLabel.setFont(new Font("Segoe UI", Font.BOLD, 36)); // Seta cresce no hover
            }

            @Override
            public void mouseExited(MouseEvent e) {
                card.putClientProperty("FlatLaf.style", cardStyle);
                arrowLabel.setFont(new Font("Segoe UI", Font.BOLD, 32)); // Seta volta ao normal
            }

            @Override
            public void mousePressed(MouseEvent e) {
                card.putClientProperty("FlatLaf.style", stylePressed);
            }

            @Override
            public void mouseReleased(MouseEvent e) {
                card.putClientProperty("FlatLaf.style", styleHover);
            }

            @Override
            public void mouseClicked(MouseEvent e) {
                action.run();
            }
        });

        return card;
    }
}

package br.analisevolumetrica.ui.components;

import br.analisevolumetrica.ui.utils.DesignConstants;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Dialog moderno para exibir progresso de operações longas
 * Com progress bar, log em tempo real e estimativa de tempo
 *
 * @author Claude Code
 */
public class ProgressDialog extends JDialog {

    private JProgressBar progressBar;
    private JLabel statusLabel;
    private JLabel timeLabel;
    private JTextArea logArea;
    private JScrollPane logScrollPane;
    private JButton cancelButton;
    private boolean cancelled = false;
    private long startTime;

    /**
     * Cria um dialog de progresso
     */
    public ProgressDialog(JFrame parent, String title) {
        super(parent, title, true);
        startTime = System.currentTimeMillis();
        createUI();
        setLocationRelativeTo(parent);
    }

    private void createUI() {
        setSize(600, 400);
        setDefaultCloseOperation(JDialog.DO_NOTHING_ON_CLOSE);
        setLayout(new BorderLayout(0, 0));

        // Painel principal
        JPanel mainPanel = new JPanel(new BorderLayout(DesignConstants.SPACING_MEDIUM, DesignConstants.SPACING_MEDIUM));
        mainPanel.setBackground(DesignConstants.BACKGROUND);
        mainPanel.setBorder(new EmptyBorder(
                DesignConstants.SPACING_LARGE,
                DesignConstants.SPACING_LARGE,
                DesignConstants.SPACING_LARGE,
                DesignConstants.SPACING_LARGE
        ));

        // Painel superior com status e tempo
        JPanel topPanel = new JPanel(new BorderLayout(DesignConstants.SPACING_SMALL, DesignConstants.SPACING_SMALL));
        topPanel.setOpaque(false);

        // Label de status
        statusLabel = new JLabel("Iniciando...");
        statusLabel.setFont(DesignConstants.FONT_BODY_BOLD);
        statusLabel.setForeground(DesignConstants.TEXT_PRIMARY);

        // Label de tempo estimado
        timeLabel = new JLabel(" ");
        timeLabel.setFont(DesignConstants.FONT_SMALL);
        timeLabel.setForeground(DesignConstants.TEXT_SECONDARY);
        timeLabel.setHorizontalAlignment(SwingConstants.RIGHT);

        topPanel.add(statusLabel, BorderLayout.WEST);
        topPanel.add(timeLabel, BorderLayout.EAST);

        // Progress bar
        progressBar = new JProgressBar(0, 100);
        progressBar.setStringPainted(true);
        progressBar.setString("0%");
        progressBar.setPreferredSize(new Dimension(0, 32));
        progressBar.putClientProperty("FlatLaf.style",
                "arc:" + DesignConstants.BORDER_RADIUS_SMALL);

        // Área de log
        logArea = new JTextArea();
        logArea.setEditable(false);
        logArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
        logArea.setBackground(Color.WHITE);
        logArea.setForeground(DesignConstants.TEXT_PRIMARY);
        logArea.setLineWrap(true);
        logArea.setWrapStyleWord(true);
        logArea.setBorder(new EmptyBorder(
                DesignConstants.SPACING_SMALL,
                DesignConstants.SPACING_SMALL,
                DesignConstants.SPACING_SMALL,
                DesignConstants.SPACING_SMALL
        ));

        logScrollPane = new JScrollPane(logArea);
        logScrollPane.setPreferredSize(new Dimension(0, 200));
        logScrollPane.putClientProperty("FlatLaf.style",
                "arc:" + DesignConstants.BORDER_RADIUS_SMALL);

        // Painel de botões
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        buttonPanel.setOpaque(false);

        cancelButton = ModernComponents.createOutlineButton("Cancelar", DesignConstants.ERROR);
        cancelButton.addActionListener(e -> {
            int confirm = JOptionPane.showConfirmDialog(
                    this,
                    "Tem certeza que deseja cancelar a operação?",
                    "Confirmar Cancelamento",
                    JOptionPane.YES_NO_OPTION,
                    JOptionPane.WARNING_MESSAGE
            );
            if (confirm == JOptionPane.YES_OPTION) {
                cancelled = true;
                cancelButton.setEnabled(false);
                appendLog("⚠️ Cancelamento solicitado pelo usuário");
            }
        });
        buttonPanel.add(cancelButton);

        // Montar painel principal
        JPanel centerPanel = new JPanel(new BorderLayout(0, DesignConstants.SPACING_MEDIUM));
        centerPanel.setOpaque(false);
        centerPanel.add(topPanel, BorderLayout.NORTH);
        centerPanel.add(progressBar, BorderLayout.CENTER);

        mainPanel.add(centerPanel, BorderLayout.NORTH);
        mainPanel.add(logScrollPane, BorderLayout.CENTER);
        mainPanel.add(buttonPanel, BorderLayout.SOUTH);

        add(mainPanel);
    }

    /**
     * Atualiza o progresso (0-100)
     */
    public void setProgress(int progress) {
        SwingUtilities.invokeLater(() -> {
            progressBar.setValue(progress);
            progressBar.setString(progress + "%");

            // Calcular tempo estimado
            if (progress > 0) {
                long elapsed = System.currentTimeMillis() - startTime;
                long estimated = (elapsed * 100) / progress;
                long remaining = estimated - elapsed;

                if (remaining > 0) {
                    String timeStr = formatTime(remaining);
                    timeLabel.setText("⏱️ Tempo estimado: " + timeStr);
                }
            }
        });
    }

    /**
     * Define o progresso como indeterminado
     */
    public void setIndeterminate(boolean indeterminate) {
        SwingUtilities.invokeLater(() -> {
            progressBar.setIndeterminate(indeterminate);
            if (indeterminate) {
                progressBar.setString("Processando...");
                timeLabel.setText("");
            }
        });
    }

    /**
     * Atualiza o texto de status
     */
    public void setStatus(String status) {
        SwingUtilities.invokeLater(() -> statusLabel.setText(status));
    }

    /**
     * Adiciona uma linha ao log
     */
    public void appendLog(String message) {
        SwingUtilities.invokeLater(() -> {
            String timestamp = new SimpleDateFormat("HH:mm:ss").format(new Date());
            logArea.append("[" + timestamp + "] " + message + "\n");

            // Auto-scroll para o final
            logArea.setCaretPosition(logArea.getDocument().getLength());
        });
    }

    /**
     * Verifica se foi cancelado
     */
    public boolean isCancelled() {
        return cancelled;
    }

    /**
     * Marca como concluído
     */
    public void setCompleted(boolean success) {
        SwingUtilities.invokeLater(() -> {
            if (success) {
                progressBar.setValue(100);
                progressBar.setString("100% - Concluído");
                statusLabel.setText("✅ Operação concluída com sucesso");
                statusLabel.setForeground(DesignConstants.SUCCESS);
            } else {
                statusLabel.setText("❌ Operação falhou");
                statusLabel.setForeground(DesignConstants.ERROR);
            }

            cancelButton.setText("Fechar");
            cancelButton.putClientProperty("FlatLaf.style", "");
            cancelButton.removeActionListener(cancelButton.getActionListeners()[0]);
            cancelButton.addActionListener(e -> dispose());

            long totalTime = System.currentTimeMillis() - startTime;
            timeLabel.setText("⏱️ Tempo total: " + formatTime(totalTime));
        });
    }

    /**
     * Formata tempo em ms para string legível
     */
    private String formatTime(long milliseconds) {
        long seconds = milliseconds / 1000;
        long minutes = seconds / 60;
        long hours = minutes / 60;

        if (hours > 0) {
            return String.format("%dh %dm %ds", hours, minutes % 60, seconds % 60);
        } else if (minutes > 0) {
            return String.format("%dm %ds", minutes, seconds % 60);
        } else {
            return String.format("%ds", seconds);
        }
    }

    /**
     * Mostra o dialog de forma não-bloqueante
     */
    public void showNonBlocking() {
        setModal(false);
        setVisible(true);
    }

    /**
     * Cria e retorna um ProgressDialog pronto para usar
     */
    public static ProgressDialog create(JFrame parent, String title, String initialStatus) {
        ProgressDialog dialog = new ProgressDialog(parent, title);
        dialog.setStatus(initialStatus);
        dialog.appendLog("Operação iniciada");
        return dialog;
    }
}

package views;

import java.awt.CardLayout;
import javax.swing.JOptionPane;
import services.PythonClient;
import com.formdev.flatlaf.themes.FlatMacLightLaf;
import java.io.File;

/**
 *
 * @author Jonas
 */
public class TelaPrincipal extends javax.swing.JFrame {

    public TelaPrincipal() {
        initComponents();
        estilizarCardsHistorico();
        estilizarBotoesHistorico();
        atualizarContadoresHistorico();
        configurarInteracaoCards();
    }
    
    private void configurarInteracaoCards() {
        adicionarEfeitoHoverCard(jCardCalibracoes, jButtonCalibracoes);
        adicionarEfeitoHoverCard(jCardVideos, jButtonVideos);
        adicionarEfeitoHoverCard(jCardFrames, jButtonFrames);
        adicionarEfeitoHoverCard(jCardVolumes, jButtonVolumes);
    }

    private void adicionarEfeitoHoverCard(javax.swing.JPanel panel, javax.swing.JButton btn) {
        String corDestaque = "#007AFF"; 
        
        // ESTILO NORMAL
        String estiloNormal = 
            "arc:16;" +
            "background:lighten(@background,3%);" +
            "border:1,1,1,1,#E0E0E0;" +
            "padding:12,12,12,12";

        // ESTILO HOVER
        String estiloHover = 
            "arc:16;" +
            "background:lighten(@background,8%);" +
            "border:2,2,2,2," + corDestaque + ";" +
            "padding:11,11,11,11";

        // 1. Configuração inicial do Painel
        panel.putClientProperty("FlatLaf.style", estiloNormal);

        // 2. Eventos do Mouse no PAINEL (Fundo do Card)
        panel.addMouseListener(new java.awt.event.MouseAdapter() {
            @Override
            public void mouseEntered(java.awt.event.MouseEvent evt) {
                panel.putClientProperty("FlatLaf.style", estiloHover);
                panel.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));
            }

            @Override
            public void mouseExited(java.awt.event.MouseEvent evt) {
                panel.putClientProperty("FlatLaf.style", estiloNormal);
                panel.setCursor(new java.awt.Cursor(java.awt.Cursor.DEFAULT_CURSOR));
            }
        });

        // 3. Eventos do Mouse no BOTÃO (Correção do Problema)
        // Quando o mouse entra no botão, ele força o Painel a ficar no estado Hover
        btn.addMouseListener(new java.awt.event.MouseAdapter() {
            @Override
            public void mouseEntered(java.awt.event.MouseEvent evt) {
                // Força o card a crescer mesmo estando sobre o botão
                panel.putClientProperty("FlatLaf.style", estiloHover);
            }

            @Override
            public void mouseExited(java.awt.event.MouseEvent evt) {
                // Lógica Inteligente:
                // Se o mouse sair do botão, mas for para o fundo do Card (Painel), 
                // NÃO voltamos ao normal. Só voltamos se sair do Card totalmente.
                java.awt.Point p = javax.swing.SwingUtilities.convertPoint(btn, evt.getPoint(), panel);
                if (!panel.contains(p)) {
                    panel.putClientProperty("FlatLaf.style", estiloNormal);
                }
            }
        });
    }
    
    private void atualizarContadoresHistorico() {
        int calibracoes = contarArquivos("../../../backend-python/data/out/calibracoes");
        int videos = contarArquivos("../../../backend-python/data/out/videos");
        int frames = contarArquivos("../../../backend-python/data/out/frames");
        int volumes = contarArquivos("../../../backend-python/data/out/volumes");

        jLabel18.setText("Calibrações: " + calibracoes);
        jLabel19.setText("Vídeos: " + videos);
        jLabel20.setText("Frames: " + frames);
        jLabel21.setText("Volumes: " + volumes);
    }
    
    private int contarArquivos(String caminho) {
        File pasta = new File(caminho);
        if (!pasta.exists() || !pasta.isDirectory()) return 0;

        File[] arquivos = pasta.listFiles(File::isFile);
        return arquivos != null ? arquivos.length : 0;
    }
    
    private void estilizarBotoesHistorico() {
        String corDestaque = "#007AFF"; // Azul Apple/Mac

        configurarBotaoOutline(jButtonCalibracoes, corDestaque); // Calibrações
        configurarBotaoOutline(jButtonVideos, corDestaque); // Vídeos
        configurarBotaoOutline(jButtonFrames, corDestaque); // Frames
        configurarBotaoOutline(jButtonVolumes, corDestaque); // Volumes
    }

    private void configurarBotaoOutline(javax.swing.JButton btn, String corHex) {
        // ESTADO NORMAL: Fundo branco, Borda Azul, Texto Azul
        String estiloNormal = 
            "arc: 12;" + 
            "background: #FFFFFF;" + 
            "foreground: " + corHex + ";" + 
            "borderWidth: 1;" + 
            "borderColor: " + corHex + ";" +
            "focusWidth: 0;" + 
            "font: bold 12";

        // ESTADO HOVER: Fundo Azul, Texto Branco (Preenche o botão)
        String estiloHover = 
            "arc: 12;" + 
            "background: " + corHex + ";" + 
            "foreground: #FFFFFF;" + 
            "borderWidth: 1;" + 
            "borderColor: " + corHex + ";" +
            "font: bold 12";

        // Aplica o estilo inicial
        btn.putClientProperty("FlatLaf.style", estiloNormal);
        btn.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        // Remove Listeners antigos para não duplicar e adiciona o novo
        for (java.awt.event.MouseListener ml : btn.getMouseListeners()) {
            btn.removeMouseListener(ml);
        }

        btn.addMouseListener(new java.awt.event.MouseAdapter() {
            @Override
            public void mouseEntered(java.awt.event.MouseEvent evt) {
                btn.putClientProperty("FlatLaf.style", estiloHover);
            }

            @Override
            public void mouseExited(java.awt.event.MouseEvent evt) {
                btn.putClientProperty("FlatLaf.style", estiloNormal);
            }
            
            @Override
            public void mousePressed(java.awt.event.MouseEvent evt) {
                // Efeito de clique (escurece um pouco)
                btn.putClientProperty("FlatLaf.style", 
                    "arc: 12; background: darken(" + corHex + ",10%); foreground: #FFFFFF; borderWidth: 0");
            }
            
            @Override
            public void mouseReleased(java.awt.event.MouseEvent evt) {
                // Volta para o estado de hover se o mouse ainda estiver em cima
                 if (btn.contains(evt.getPoint())) {
                     btn.putClientProperty("FlatLaf.style", estiloHover);
                 } else {
                     btn.putClientProperty("FlatLaf.style", estiloNormal);
                 }
            }
        });
    }
    
    private void estilizarCardsHistorico() {
        String cardStyle =
            "arc:16;" +
            "background:lighten(@background,3%);" +
            "border:1,1,1,1,#E0E0E0";

        jCardCalibracoes.putClientProperty("FlatLaf.style", cardStyle);
        jCardVideos.putClientProperty("FlatLaf.style", cardStyle);
        jCardFrames.putClientProperty("FlatLaf.style", cardStyle);
        jCardVolumes.putClientProperty("FlatLaf.style", cardStyle);
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        jPanelWelcome = new javax.swing.JPanel();
        jPanelWELCOME2 = new javax.swing.JPanel();
        jLabel2 = new javax.swing.JLabel();
        jLabel3 = new javax.swing.JLabel();
        jLabel4 = new javax.swing.JLabel();
        jLabel5 = new javax.swing.JLabel();
        jLabel6 = new javax.swing.JLabel();
        jLabel7 = new javax.swing.JLabel();
        jLabel8 = new javax.swing.JLabel();
        jLabel9 = new javax.swing.JLabel();
        jLabel12 = new javax.swing.JLabel();
        jPanelSobre = new javax.swing.JPanel();
        jLabel10 = new javax.swing.JLabel();
        jLabel11 = new javax.swing.JLabel();
        jLabel13 = new javax.swing.JLabel();
        jLabel14 = new javax.swing.JLabel();
        jLabel15 = new javax.swing.JLabel();
        jLabel22 = new javax.swing.JLabel();
        jLabel1 = new javax.swing.JLabel();
        jPanelHistorico = new javax.swing.JPanel();
        jLabel16 = new javax.swing.JLabel();
        jLabel23 = new javax.swing.JLabel();
        jCardCalibracoes = new javax.swing.JPanel();
        jLabel18 = new javax.swing.JLabel();
        jButtonCalibracoes = new javax.swing.JButton();
        jCardVideos = new javax.swing.JPanel();
        jLabel19 = new javax.swing.JLabel();
        jButtonVideos = new javax.swing.JButton();
        jCardFrames = new javax.swing.JPanel();
        jLabel20 = new javax.swing.JLabel();
        jButtonFrames = new javax.swing.JButton();
        jCardVolumes = new javax.swing.JPanel();
        jLabel21 = new javax.swing.JLabel();
        jButtonVolumes = new javax.swing.JButton();
        jPanelTutorial = new javax.swing.JPanel();
        jLabel1TUTORIAL = new javax.swing.JLabel();
        jMenuBar = new javax.swing.JMenuBar();
        jMenuIniciar = new javax.swing.JMenu();
        jMenuItemWelcome = new javax.swing.JMenuItem();
        jMenuItemRunWithout = new javax.swing.JMenuItem();
        jMenuItemRunWith = new javax.swing.JMenuItem();
        jMenuItemCalibracao = new javax.swing.JMenuItem();
        jMenuItemExtracao = new javax.swing.JMenuItem();
        jMenuItemReconstrucao = new javax.swing.JMenuItem();
        jMenuHistorico = new javax.swing.JMenu();
        jMenuTutorial = new javax.swing.JMenu();
        jMenuSobre = new javax.swing.JMenu();
        jMenuSair = new javax.swing.JMenu();

        setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
        setMaximumSize(new java.awt.Dimension(1920, 1080));
        setMinimumSize(new java.awt.Dimension(800, 600));
        setPreferredSize(new java.awt.Dimension(900, 600));
        setResizable(false);

        jPanelWelcome.setMaximumSize(new java.awt.Dimension(1280, 720));
        jPanelWelcome.setMinimumSize(new java.awt.Dimension(800, 600));
        jPanelWelcome.setLayout(new java.awt.CardLayout());

        jPanelWELCOME2.setPreferredSize(new java.awt.Dimension(850, 600));

        jLabel2.setFont(new java.awt.Font("Segoe UI", 1, 24)); // NOI18N
        jLabel2.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        jLabel2.setText("Bem-vindo ao [Nome do Aplicativo]!");

        jLabel3.setFont(new java.awt.Font("Segoe UI", 0, 18)); // NOI18N
        jLabel3.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        jLabel3.setText("<html> <div style=\"text-align: center;\">Este aplicativo foi desenvolvido para realizar análise volumétrica de objetos por meio de técnicas de visão computacional, permitindo o cálculo de volumes a partir do processamento e análise de imagens. </div>   </html>");
        jLabel3.setToolTipText("");

        jLabel4.setFont(new java.awt.Font("Segoe UI", 0, 16)); // NOI18N
        jLabel4.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/application.png"))); // NOI18N
        jLabel4.setText("<html><b>Iniciar:</b> Comece aqui. Carregue um novo arquivo de vídeo para realizar a reconstrução 3D e o cálculo volumétrico.</html>");

        jLabel5.setFont(new java.awt.Font("Segoe UI", 0, 16)); // NOI18N
        jLabel5.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/database.png"))); // NOI18N
        jLabel5.setText("<html><b>Histórico:</b> Acesse o banco de dados de análises anteriores, visualize resultados salvos e métricas de processamento.</html>");

        jLabel6.setFont(new java.awt.Font("Segoe UI", 0, 16)); // NOI18N
        jLabel6.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/application_xp_terminal.png"))); // NOI18N
        jLabel6.setText("<html><b>Tutorial:</b> Dúvidas na captura? Veja o guia passo a passo de como filmar o objeto para obter a melhor precisão.</html>");

        jLabel7.setFont(new java.awt.Font("Segoe UI", 0, 16)); // NOI18N
        jLabel7.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/information.png"))); // NOI18N
        jLabel7.setText("<html><b>Sobre:</b> Conheça a tecnologia por trás do projeto e a equipe de desenvolvimento.</html>");

        jLabel8.setFont(new java.awt.Font("Segoe UI", 0, 16)); // NOI18N
        jLabel8.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/cross.png"))); // NOI18N
        jLabel8.setText("<html><b>Sair:</b> Encerrar o aplicativo.</html>");

        jLabel9.setFont(new java.awt.Font("Segoe UI", 0, 18)); // NOI18N
        jLabel9.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        jLabel9.setText("<html> <div style=\"text-align: center;\">Para navegar, utilize o menu superior. Aqui está o que você pode fazer: </div> </html>");

        jLabel12.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        jLabel12.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/money.png"))); // NOI18N
        jLabel12.setText("AJUDE-NOS: ");

        javax.swing.GroupLayout jPanelWELCOME2Layout = new javax.swing.GroupLayout(jPanelWELCOME2);
        jPanelWELCOME2.setLayout(jPanelWELCOME2Layout);
        jPanelWELCOME2Layout.setHorizontalGroup(
            jPanelWELCOME2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanelWELCOME2Layout.createSequentialGroup()
                .addGroup(jPanelWELCOME2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(jLabel3, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                    .addGroup(jPanelWELCOME2Layout.createSequentialGroup()
                        .addContainerGap()
                        .addGroup(jPanelWELCOME2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel4)
                            .addComponent(jLabel6)
                            .addComponent(jLabel7)
                            .addComponent(jLabel2, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                            .addComponent(jLabel8)
                            .addComponent(jLabel5, javax.swing.GroupLayout.DEFAULT_SIZE, 838, Short.MAX_VALUE)
                            .addComponent(jLabel9))))
                .addContainerGap())
            .addGroup(jPanelWELCOME2Layout.createSequentialGroup()
                .addGap(59, 59, 59)
                .addComponent(jLabel12, javax.swing.GroupLayout.PREFERRED_SIZE, 777, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );
        jPanelWELCOME2Layout.setVerticalGroup(
            jPanelWELCOME2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelWELCOME2Layout.createSequentialGroup()
                .addGap(17, 17, 17)
                .addComponent(jLabel2, javax.swing.GroupLayout.PREFERRED_SIZE, 65, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel3, javax.swing.GroupLayout.PREFERRED_SIZE, 80, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel12, javax.swing.GroupLayout.DEFAULT_SIZE, 64, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel9, javax.swing.GroupLayout.PREFERRED_SIZE, 53, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel4, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel5, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel6, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel7, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel8, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(73, 73, 73))
        );

        jPanelWelcome.add(jPanelWELCOME2, "telaInicial");

        jPanelSobre.setPreferredSize(new java.awt.Dimension(850, 600));

        jLabel10.setFont(new java.awt.Font("Segoe UI", 1, 24)); // NOI18N
        jLabel10.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        jLabel10.setText("Sobre o Projeto");

        jLabel11.setFont(new java.awt.Font("Segoe UI", 0, 17)); // NOI18N
        jLabel11.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        jLabel11.setText("<html> <div style=\"text-align: center\"> \n<b>Java Swing:</b> Interface gráfica do usuário (GUI). <br>         \n<b>Python:</b> Backend e processamento numérico. <br>         \n<b>Flask API:</b> Comunicação entre Interface e Backend. <br>         \n<b>OpenCV:</b> Processamento e análise de imagens. <br>         \n<b>Open3D:</b> Manipulação de nuvens de pontos e malhas. <br>         \n<b>SfM (COLMAP):</b> Reconstrução 3D a partir de múltiplas imagens.\n</div> </html>");

        jLabel13.setFont(new java.awt.Font("Segoe UI", 0, 16)); // NOI18N
        jLabel13.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        jLabel13.setText("<html>\n<table align=\"center\" cellspacing=\"10\"> <tr>\n        <td align=\"center\">Jonas Campos</td> <td>-</td> <td align=\"center\">Bruno Henrique</td> <td>-</td> <td align=\"center\">Tiago Douglas</td>\n    </tr>\n    <tr>\n        <td align=\"center\">Sofia Lacorti</td> <td>-</td> <td align=\"center\">Mateus Diniz</td> <td>-</td> <td align=\"center\">Zeca Manuel</td>\n    </tr>\n</table>\n</html>");

        jLabel14.setFont(new java.awt.Font("Segoe UI", 1, 22)); // NOI18N
        jLabel14.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        jLabel14.setText("Tecnologias utilizadas");

        jLabel15.setFont(new java.awt.Font("Segoe UI", 1, 22)); // NOI18N
        jLabel15.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        jLabel15.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/UFOP-removebg-preview (1).png"))); // NOI18N
        jLabel15.setText("Equipe de desenvolvimento");

        jLabel22.setFont(new java.awt.Font("Segoe UI", 0, 18)); // NOI18N
        jLabel22.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        jLabel22.setText("<html> <div style=\"text-align: center\"> \n<p>O <b>[Nome do Aplicativo]</b> é um software desenvolvido para reconstrução 3D e estimativa de volume a <br>partir de arquivos de vídeo, utilizando Visão Computacional.</p>\n\n</div></html>");
        jLabel22.setToolTipText("");
        jLabel22.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);

        jLabel1.setFont(new java.awt.Font("Segoe UI", 2, 16)); // NOI18N
        jLabel1.setText("<HTML>Código disponível em: <a href=\"https://github.com/BrunoHPS7/AnaliseVolumetrica/\">GitHub</a></HTML>");

        javax.swing.GroupLayout jPanelSobreLayout = new javax.swing.GroupLayout(jPanelSobre);
        jPanelSobre.setLayout(jPanelSobreLayout);
        jPanelSobreLayout.setHorizontalGroup(
            jPanelSobreLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelSobreLayout.createSequentialGroup()
                .addGroup(jPanelSobreLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel22, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.DEFAULT_SIZE, 894, Short.MAX_VALUE)
                    .addGroup(jPanelSobreLayout.createSequentialGroup()
                        .addGroup(jPanelSobreLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel15, javax.swing.GroupLayout.PREFERRED_SIZE, 417, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addGroup(jPanelSobreLayout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jLabel13, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(jLabel1, javax.swing.GroupLayout.PREFERRED_SIZE, 216, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(17, 17, 17))
                    .addGroup(jPanelSobreLayout.createSequentialGroup()
                        .addContainerGap()
                        .addGroup(jPanelSobreLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel10, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                            .addComponent(jLabel14, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)))
                    .addComponent(jLabel11, javax.swing.GroupLayout.Alignment.TRAILING))
                .addContainerGap())
        );
        jPanelSobreLayout.setVerticalGroup(
            jPanelSobreLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelSobreLayout.createSequentialGroup()
                .addGap(17, 17, 17)
                .addComponent(jLabel10, javax.swing.GroupLayout.PREFERRED_SIZE, 65, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel22, javax.swing.GroupLayout.PREFERRED_SIZE, 80, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jLabel14, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel11, javax.swing.GroupLayout.PREFERRED_SIZE, 157, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(40, 40, 40)
                .addGroup(jPanelSobreLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addGroup(jPanelSobreLayout.createSequentialGroup()
                        .addComponent(jLabel15, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jLabel13, javax.swing.GroupLayout.PREFERRED_SIZE, 70, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(jLabel1, javax.swing.GroupLayout.PREFERRED_SIZE, 28, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap(55, Short.MAX_VALUE))
        );

        jPanelWelcome.add(jPanelSobre, "telaSobre");

        jPanelHistorico.setPreferredSize(new java.awt.Dimension(850, 600));

        jLabel16.setFont(new java.awt.Font("Segoe UI", 1, 24)); // NOI18N
        jLabel16.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        jLabel16.setText("Histórico de Dados");

        jLabel23.setFont(new java.awt.Font("Segoe UI", 0, 18)); // NOI18N
        jLabel23.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        jLabel23.setText("<html> <div style=\"text-align: center;\">Gerencie os recursos utilizados nas reconstruções. Selecione uma categoria abaixo para visualizar os<br> logs de calibrações de câmera, vídeos processados e frames extraídos. </div>   </html>");
        jLabel23.setToolTipText("");

        jCardCalibracoes.setPreferredSize(new java.awt.Dimension(150, 100));

        jLabel18.setFont(new java.awt.Font("Segoe UI", 0, 15)); // NOI18N
        jLabel18.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/camera.png"))); // NOI18N
        jLabel18.setText("Calibrações");

        jButtonCalibracoes.setFont(new java.awt.Font("Segoe UI", 0, 15)); // NOI18N
        jButtonCalibracoes.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/folder.png"))); // NOI18N
        jButtonCalibracoes.setText("Acessar");
        jButtonCalibracoes.setPreferredSize(new java.awt.Dimension(100, 30));
        jButtonCalibracoes.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButtonCalibracoesActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jCardCalibracoesLayout = new javax.swing.GroupLayout(jCardCalibracoes);
        jCardCalibracoes.setLayout(jCardCalibracoesLayout);
        jCardCalibracoesLayout.setHorizontalGroup(
            jCardCalibracoesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jCardCalibracoesLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jCardCalibracoesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel18, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jButtonCalibracoes, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.DEFAULT_SIZE, 138, Short.MAX_VALUE))
                .addContainerGap())
        );
        jCardCalibracoesLayout.setVerticalGroup(
            jCardCalibracoesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jCardCalibracoesLayout.createSequentialGroup()
                .addGap(12, 12, 12)
                .addComponent(jLabel18)
                .addGap(18, 18, 18)
                .addComponent(jButtonCalibracoes, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        jCardVideos.setPreferredSize(new java.awt.Dimension(150, 100));

        jLabel19.setFont(new java.awt.Font("Segoe UI", 0, 15)); // NOI18N
        jLabel19.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/film.png"))); // NOI18N
        jLabel19.setText("Vídeos");

        jButtonVideos.setFont(new java.awt.Font("Segoe UI", 0, 15)); // NOI18N
        jButtonVideos.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/folder.png"))); // NOI18N
        jButtonVideos.setText("Acessar");
        jButtonVideos.setPreferredSize(new java.awt.Dimension(100, 30));
        jButtonVideos.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButtonVideosActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jCardVideosLayout = new javax.swing.GroupLayout(jCardVideos);
        jCardVideos.setLayout(jCardVideosLayout);
        jCardVideosLayout.setHorizontalGroup(
            jCardVideosLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jCardVideosLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jCardVideosLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jButtonVideos, javax.swing.GroupLayout.DEFAULT_SIZE, 138, Short.MAX_VALUE)
                    .addComponent(jLabel19, javax.swing.GroupLayout.DEFAULT_SIZE, 138, Short.MAX_VALUE))
                .addContainerGap())
        );
        jCardVideosLayout.setVerticalGroup(
            jCardVideosLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jCardVideosLayout.createSequentialGroup()
                .addGap(12, 12, 12)
                .addComponent(jLabel19)
                .addGap(18, 18, 18)
                .addComponent(jButtonVideos, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(19, Short.MAX_VALUE))
        );

        jCardFrames.setPreferredSize(new java.awt.Dimension(150, 100));

        jLabel20.setFont(new java.awt.Font("Segoe UI", 0, 15)); // NOI18N
        jLabel20.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/photo.png"))); // NOI18N
        jLabel20.setText("Frames");

        jButtonFrames.setFont(new java.awt.Font("Segoe UI", 0, 15)); // NOI18N
        jButtonFrames.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/folder.png"))); // NOI18N
        jButtonFrames.setText("Acessar");
        jButtonFrames.setPreferredSize(new java.awt.Dimension(100, 30));
        jButtonFrames.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButtonFramesActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jCardFramesLayout = new javax.swing.GroupLayout(jCardFrames);
        jCardFrames.setLayout(jCardFramesLayout);
        jCardFramesLayout.setHorizontalGroup(
            jCardFramesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jCardFramesLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jCardFramesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel20, javax.swing.GroupLayout.DEFAULT_SIZE, 138, Short.MAX_VALUE)
                    .addComponent(jButtonFrames, javax.swing.GroupLayout.DEFAULT_SIZE, 138, Short.MAX_VALUE))
                .addContainerGap())
        );
        jCardFramesLayout.setVerticalGroup(
            jCardFramesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jCardFramesLayout.createSequentialGroup()
                .addGap(12, 12, 12)
                .addComponent(jLabel20)
                .addGap(18, 18, 18)
                .addComponent(jButtonFrames, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        jCardVolumes.setPreferredSize(new java.awt.Dimension(150, 100));

        jLabel21.setFont(new java.awt.Font("Segoe UI", 0, 15)); // NOI18N
        jLabel21.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/calculator.png"))); // NOI18N
        jLabel21.setText("Volumes");

        jButtonVolumes.setFont(new java.awt.Font("Segoe UI", 0, 15)); // NOI18N
        jButtonVolumes.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/folder.png"))); // NOI18N
        jButtonVolumes.setText("Acessar");
        jButtonVolumes.setPreferredSize(new java.awt.Dimension(100, 30));
        jButtonVolumes.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButtonVolumesActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jCardVolumesLayout = new javax.swing.GroupLayout(jCardVolumes);
        jCardVolumes.setLayout(jCardVolumesLayout);
        jCardVolumesLayout.setHorizontalGroup(
            jCardVolumesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jCardVolumesLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jCardVolumesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jButtonVolumes, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jLabel21, javax.swing.GroupLayout.DEFAULT_SIZE, 138, Short.MAX_VALUE))
                .addContainerGap())
        );
        jCardVolumesLayout.setVerticalGroup(
            jCardVolumesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jCardVolumesLayout.createSequentialGroup()
                .addGap(12, 12, 12)
                .addComponent(jLabel21)
                .addGap(18, 18, 18)
                .addComponent(jButtonVolumes, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        javax.swing.GroupLayout jPanelHistoricoLayout = new javax.swing.GroupLayout(jPanelHistorico);
        jPanelHistorico.setLayout(jPanelHistoricoLayout);
        jPanelHistoricoLayout.setHorizontalGroup(
            jPanelHistoricoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanelHistoricoLayout.createSequentialGroup()
                .addGap(0, 0, Short.MAX_VALUE)
                .addComponent(jCardCalibracoes, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jCardVideos, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jCardFrames, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jCardVolumes, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(125, 125, 125))
            .addGroup(jPanelHistoricoLayout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel16, javax.swing.GroupLayout.DEFAULT_SIZE, 838, Short.MAX_VALUE)
                .addContainerGap())
            .addGroup(jPanelHistoricoLayout.createSequentialGroup()
                .addComponent(jLabel23, javax.swing.GroupLayout.DEFAULT_SIZE, 894, Short.MAX_VALUE)
                .addContainerGap())
        );
        jPanelHistoricoLayout.setVerticalGroup(
            jPanelHistoricoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelHistoricoLayout.createSequentialGroup()
                .addGap(17, 17, 17)
                .addComponent(jLabel16, javax.swing.GroupLayout.PREFERRED_SIZE, 65, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel23, javax.swing.GroupLayout.PREFERRED_SIZE, 80, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(52, 52, 52)
                .addGroup(jPanelHistoricoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(jCardFrames, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jCardCalibracoes, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jCardVolumes, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jCardVideos, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap(280, Short.MAX_VALUE))
        );

        jPanelWelcome.add(jPanelHistorico, "telaHistorico");

        jPanelTutorial.setPreferredSize(new java.awt.Dimension(850, 600));

        jLabel1TUTORIAL.setText("JPANEL TUTORIAL");

        javax.swing.GroupLayout jPanelTutorialLayout = new javax.swing.GroupLayout(jPanelTutorial);
        jPanelTutorial.setLayout(jPanelTutorialLayout);
        jPanelTutorialLayout.setHorizontalGroup(
            jPanelTutorialLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelTutorialLayout.createSequentialGroup()
                .addGap(321, 321, 321)
                .addComponent(jLabel1TUTORIAL, javax.swing.GroupLayout.PREFERRED_SIZE, 329, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(250, Short.MAX_VALUE))
        );
        jPanelTutorialLayout.setVerticalGroup(
            jPanelTutorialLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelTutorialLayout.createSequentialGroup()
                .addGap(208, 208, 208)
                .addComponent(jLabel1TUTORIAL, javax.swing.GroupLayout.PREFERRED_SIZE, 204, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(188, Short.MAX_VALUE))
        );

        jPanelWelcome.add(jPanelTutorial, "telaTutorial");

        jMenuIniciar.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/application.png"))); // NOI18N
        jMenuIniciar.setText("Iniciar");

        jMenuItemWelcome.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/house.png"))); // NOI18N
        jMenuItemWelcome.setText("Menu inicial");
        jMenuItemWelcome.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItemWelcomeActionPerformed(evt);
            }
        });
        jMenuIniciar.add(jMenuItemWelcome);

        jMenuItemRunWithout.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/application_go.png"))); // NOI18N
        jMenuItemRunWithout.setText("Execução normal");
        jMenuItemRunWithout.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItemRunWithoutActionPerformed(evt);
            }
        });
        jMenuIniciar.add(jMenuItemRunWithout);

        jMenuItemRunWith.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/application_view_tile.png"))); // NOI18N
        jMenuItemRunWith.setText("Execução com tutorial");
        jMenuIniciar.add(jMenuItemRunWith);

        jMenuItemCalibracao.setText("Calibração da câmera");
        jMenuItemCalibracao.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItemCalibracaoActionPerformed(evt);
            }
        });
        jMenuIniciar.add(jMenuItemCalibracao);

        jMenuItemExtracao.setText("Extração de frames");
        jMenuItemExtracao.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItemExtracaoActionPerformed(evt);
            }
        });
        jMenuIniciar.add(jMenuItemExtracao);

        jMenuItemReconstrucao.setText("Reconstrução da cena");
        jMenuItemReconstrucao.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItemReconstrucaoActionPerformed(evt);
            }
        });
        jMenuIniciar.add(jMenuItemReconstrucao);

        jMenuBar.add(jMenuIniciar);

        jMenuHistorico.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/database.png"))); // NOI18N
        jMenuHistorico.setText("Histórico");
        jMenuHistorico.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                jMenuHistoricoMouseClicked(evt);
            }
        });
        jMenuBar.add(jMenuHistorico);

        jMenuTutorial.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/application_xp_terminal.png"))); // NOI18N
        jMenuTutorial.setText("Tutorial");
        jMenuTutorial.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                jMenuTutorialMouseClicked(evt);
            }
        });
        jMenuBar.add(jMenuTutorial);

        jMenuSobre.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/information.png"))); // NOI18N
        jMenuSobre.setText("Sobre");
        jMenuSobre.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                jMenuSobreMouseClicked(evt);
            }
        });
        jMenuBar.add(jMenuSobre);

        jMenuSair.setIcon(new javax.swing.ImageIcon(getClass().getResource("/images/icons/cross.png"))); // NOI18N
        jMenuSair.setText("Sair");
        jMenuSair.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                jMenuSairMouseClicked(evt);
            }
        });
        jMenuBar.add(jMenuSair);

        setJMenuBar(jMenuBar);

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jPanelWelcome, javax.swing.GroupLayout.PREFERRED_SIZE, 900, javax.swing.GroupLayout.PREFERRED_SIZE)
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jPanelWelcome, javax.swing.GroupLayout.PREFERRED_SIZE, 600, javax.swing.GroupLayout.PREFERRED_SIZE)
        );

        pack();
        setLocationRelativeTo(null);
    }// </editor-fold>//GEN-END:initComponents
    
    private void jMenuTutorialMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jMenuTutorialMouseClicked
        // TODO add your handling code here:
        CardLayout cl = (CardLayout) jPanelWelcome.getLayout();
        cl.show(jPanelWelcome, "telaTutorial");
        
        jMenuTutorial.setSelected(false);
        jPanelWelcome.requestFocusInWindow();
        
    }//GEN-LAST:event_jMenuTutorialMouseClicked

    private void jMenuSairMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jMenuSairMouseClicked
        // TODO add your handling code here:
        
        jMenuSair.setSelected(false);
        jPanelWelcome.requestFocusInWindow();
        
        Object[] opcoes = {"Sim", "Cancelar"};
        
        int opcao = JOptionPane.showOptionDialog(
                this, 
                "Deseja sair do sistema?", 
                "Confirmação", 
                JOptionPane.DEFAULT_OPTION, 
                JOptionPane.WARNING_MESSAGE, 
                null,
                opcoes, 
                opcoes[1]
        );
        
        if (opcao == 0) {
            System.exit(0);
        }
    }//GEN-LAST:event_jMenuSairMouseClicked

    private void jMenuSobreMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jMenuSobreMouseClicked
        // TODO add your handling code here:
        CardLayout cl = (CardLayout) jPanelWelcome.getLayout();
        cl.show(jPanelWelcome, "telaSobre");
        
        jMenuSobre.setSelected(false);
        jPanelWelcome.requestFocusInWindow();
        
    }//GEN-LAST:event_jMenuSobreMouseClicked

    private void jMenuHistoricoMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jMenuHistoricoMouseClicked
        // TODO add your handling code here:
        CardLayout cl = (CardLayout) jPanelWelcome.getLayout();
        cl.show(jPanelWelcome, "telaHistorico");
        
        jMenuHistorico.setSelected(false);    // Remove o estado visual de "selecionado"
        jPanelWelcome.requestFocusInWindow();
        
    }//GEN-LAST:event_jMenuHistoricoMouseClicked

    private void jMenuItemCalibracaoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItemCalibracaoActionPerformed
        // TODO add your handling code here:
        try {
            String resposta = PythonClient.calibrarCamera();
            JOptionPane.showMessageDialog(this, resposta);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Erro ao executar calibração");
        }
    }//GEN-LAST:event_jMenuItemCalibracaoActionPerformed

    private void jMenuItemExtracaoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItemExtracaoActionPerformed
        // TODO add your handling code here:
        try {
            String resposta = PythonClient.extrairFrames();
            JOptionPane.showMessageDialog(this, resposta);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Erro ao executar extração");
        }
    }//GEN-LAST:event_jMenuItemExtracaoActionPerformed

    private void jMenuItemReconstrucaoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItemReconstrucaoActionPerformed
        // TODO add your handling code here:
        try {
            String resposta = PythonClient.reconstruir();
            JOptionPane.showMessageDialog(this, resposta);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Erro ao executar reconstrução");
        }
    }//GEN-LAST:event_jMenuItemReconstrucaoActionPerformed

    private void jMenuItemWelcomeActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItemWelcomeActionPerformed
        // TODO add your handling code here:
        CardLayout cl = (CardLayout) jPanelWelcome.getLayout();
        cl.show(jPanelWelcome, "telaInicial");
    }//GEN-LAST:event_jMenuItemWelcomeActionPerformed

    private void jButtonCalibracoesActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonCalibracoesActionPerformed
        // TODO add your handling code here:
        try {
            String resposta = PythonClient.historico();
            JOptionPane.showMessageDialog(this, resposta);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Erro ao abrir o histórico");
        }
    }//GEN-LAST:event_jButtonCalibracoesActionPerformed

    private void jButtonVideosActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonVideosActionPerformed
        // TODO add your handling code here:
        try {
            String resposta = PythonClient.historico();
            JOptionPane.showMessageDialog(this, resposta);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Erro ao abrir o histórico");
        }
    }//GEN-LAST:event_jButtonVideosActionPerformed

    private void jButtonFramesActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonFramesActionPerformed
        // TODO add your handling code here:
        try {
            String resposta = PythonClient.historico();
            JOptionPane.showMessageDialog(this, resposta);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Erro ao abrir o histórico");
        }
    }//GEN-LAST:event_jButtonFramesActionPerformed

    private void jButtonVolumesActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonVolumesActionPerformed
        // TODO add your handling code here:
        try {
            String resposta = PythonClient.historico();
            JOptionPane.showMessageDialog(this, resposta);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Erro ao abrir o histórico");
        }
    }//GEN-LAST:event_jButtonVolumesActionPerformed

    private void jMenuItemRunWithoutActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItemRunWithoutActionPerformed
        // TODO add your handling code here:
        try {
            String resposta = PythonClient.execucaoNormal();
            JOptionPane.showMessageDialog(this, resposta);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Erro ao executar o programa");
        }
    }//GEN-LAST:event_jMenuItemRunWithoutActionPerformed

    /**
     * @param args the command line arguments
     */
    public static void main(String args[]) {
        
        FlatMacLightLaf.setup();
        //</editor-fold>
        
        javax.swing.UIManager.put("Component.arc", 12);
        javax.swing.UIManager.put("Button.arc", 12);
        javax.swing.UIManager.put("TextComponent.arc", 10);
        javax.swing.UIManager.put("ScrollBar.width", 14);

        
        /* Create and display the form */
        java.awt.EventQueue.invokeLater(new Runnable() {
            public void run() {
                new TelaPrincipal().setVisible(true);
            }
        });
    }

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton jButtonCalibracoes;
    private javax.swing.JButton jButtonFrames;
    private javax.swing.JButton jButtonVideos;
    private javax.swing.JButton jButtonVolumes;
    private javax.swing.JPanel jCardCalibracoes;
    private javax.swing.JPanel jCardFrames;
    private javax.swing.JPanel jCardVideos;
    private javax.swing.JPanel jCardVolumes;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel10;
    private javax.swing.JLabel jLabel11;
    private javax.swing.JLabel jLabel12;
    private javax.swing.JLabel jLabel13;
    private javax.swing.JLabel jLabel14;
    private javax.swing.JLabel jLabel15;
    private javax.swing.JLabel jLabel16;
    private javax.swing.JLabel jLabel18;
    private javax.swing.JLabel jLabel19;
    private javax.swing.JLabel jLabel1TUTORIAL;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel20;
    private javax.swing.JLabel jLabel21;
    private javax.swing.JLabel jLabel22;
    private javax.swing.JLabel jLabel23;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel8;
    private javax.swing.JLabel jLabel9;
    private javax.swing.JMenuBar jMenuBar;
    private javax.swing.JMenu jMenuHistorico;
    private javax.swing.JMenu jMenuIniciar;
    private javax.swing.JMenuItem jMenuItemCalibracao;
    private javax.swing.JMenuItem jMenuItemExtracao;
    private javax.swing.JMenuItem jMenuItemReconstrucao;
    private javax.swing.JMenuItem jMenuItemRunWith;
    private javax.swing.JMenuItem jMenuItemRunWithout;
    private javax.swing.JMenuItem jMenuItemWelcome;
    private javax.swing.JMenu jMenuSair;
    private javax.swing.JMenu jMenuSobre;
    private javax.swing.JMenu jMenuTutorial;
    private javax.swing.JPanel jPanelHistorico;
    private javax.swing.JPanel jPanelSobre;
    private javax.swing.JPanel jPanelTutorial;
    private javax.swing.JPanel jPanelWELCOME2;
    private javax.swing.JPanel jPanelWelcome;
    // End of variables declaration//GEN-END:variables
}

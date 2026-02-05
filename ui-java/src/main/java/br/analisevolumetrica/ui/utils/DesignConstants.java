package br.analisevolumetrica.ui.utils;

import java.awt.Color;
import java.awt.Font;

/**
 * Constantes de design para interface moderna e consistente
 * Paleta de cores, fontes e dimensões padronizadas
 *
 * @author Claude Code
 */
public class DesignConstants {

    // ============ CORES PRIMÁRIAS ============
    public static final Color PRIMARY = new Color(79, 70, 229);        // #4F46E5 Indigo
    public static final Color PRIMARY_HOVER = new Color(99, 102, 241); // #6366F1
    public static final Color PRIMARY_DARK = new Color(55, 48, 163);   // #3730A3

    // ============ CORES DE ESTADO ============
    public static final Color SUCCESS = new Color(16, 185, 129);       // #10B981
    public static final Color WARNING = new Color(245, 158, 11);       // #F59E0B
    public static final Color ERROR = new Color(239, 68, 68);          // #EF4444
    public static final Color INFO = new Color(59, 130, 246);          // #3B82F6

    // ============ CORES NEUTRAS ============
    public static final Color TEXT_PRIMARY = new Color(31, 41, 55);    // #1F2937
    public static final Color TEXT_SECONDARY = new Color(107, 114, 128); // #6B7280
    public static final Color BORDER = new Color(229, 231, 235);       // #E5E7EB
    public static final Color BACKGROUND = new Color(249, 250, 251);   // #F9FAFB
    public static final Color CARD_BG = Color.WHITE;                   // #FFFFFF

    // ============ CORES DE DESTAQUE (para categorias) ============
    public static final Color CATEGORY_VIDEO = new Color(139, 92, 246);      // #8B5CF6 Roxo
    public static final Color CATEGORY_CALIBRATION = new Color(236, 72, 153); // #EC4899 Rosa
    public static final Color CATEGORY_RECONSTRUCTION = new Color(20, 184, 166); // #14B8A6 Teal
    public static final Color CATEGORY_VOLUME = new Color(249, 115, 22);      // #F97316 Laranja

    // ============ HEX STRINGS (para FlatLaf styles) ============
    public static final String HEX_PRIMARY = "#4F46E5";
    public static final String HEX_PRIMARY_HOVER = "#6366F1";
    public static final String HEX_PRIMARY_DARK = "#3730A3";
    public static final String HEX_SUCCESS = "#10B981";
    public static final String HEX_WARNING = "#F59E0B";
    public static final String HEX_ERROR = "#EF4444";
    public static final String HEX_INFO = "#3B82F6";
    public static final String HEX_TEXT_PRIMARY = "#1F2937";
    public static final String HEX_TEXT_SECONDARY = "#6B7280";
    public static final String HEX_BORDER = "#E5E7EB";
    public static final String HEX_BACKGROUND = "#F9FAFB";
    public static final String HEX_CARD_BG = "#FFFFFF";

    // Categorias
    public static final String HEX_CATEGORY_VIDEO = "#8B5CF6";
    public static final String HEX_CATEGORY_CALIBRATION = "#EC4899";
    public static final String HEX_CATEGORY_RECONSTRUCTION = "#14B8A6";
    public static final String HEX_CATEGORY_VOLUME = "#F97316";

    // ============ FONTES ============
    public static final Font FONT_TITLE = new Font("Segoe UI", Font.BOLD, 28);
    public static final Font FONT_HEADING = new Font("Segoe UI", Font.BOLD, 20);
    public static final Font FONT_SUBHEADING = new Font("Segoe UI", Font.BOLD, 16);
    public static final Font FONT_BODY = new Font("Segoe UI", Font.PLAIN, 14);
    public static final Font FONT_BODY_BOLD = new Font("Segoe UI", Font.BOLD, 14);
    public static final Font FONT_SMALL = new Font("Segoe UI", Font.PLAIN, 12);
    public static final Font FONT_SMALL_BOLD = new Font("Segoe UI", Font.BOLD, 12);
    public static final Font FONT_TINY = new Font("Segoe UI", Font.PLAIN, 10);

    // ============ DIMENSÕES ============
    public static final int BORDER_RADIUS_LARGE = 20;
    public static final int BORDER_RADIUS_MEDIUM = 16;
    public static final int BORDER_RADIUS_SMALL = 12;
    public static final int BORDER_RADIUS_TINY = 8;

    public static final int SPACING_TINY = 4;
    public static final int SPACING_SMALL = 8;
    public static final int SPACING_MEDIUM = 16;
    public static final int SPACING_LARGE = 24;
    public static final int SPACING_XLARGE = 32;

    public static final int CARD_MIN_WIDTH = 240;
    public static final int CARD_MIN_HEIGHT = 200;

    // ============ SOMBRAS (para bordas) ============
    public static final int SHADOW_SMALL = 2;
    public static final int SHADOW_MEDIUM = 4;
    public static final int SHADOW_LARGE = 8;

    // ============ ÍCONES (emojis modernos como fallback) ============
    public static final String ICON_VIDEO = "📹";
    public static final String ICON_FOLDER = "📂";
    public static final String ICON_CALCULATOR = "📊";
    public static final String ICON_HISTORY = "📚";
    public static final String ICON_SUCCESS = "✅";
    public static final String ICON_ERROR = "❌";
    public static final String ICON_WARNING = "⚠️";
    public static final String ICON_INFO = "ℹ️";
    public static final String ICON_CONNECTED = "●";
    public static final String ICON_DISCONNECTED = "○";
    public static final String ICON_ROCKET = "🚀";

    /**
     * Escurece uma cor
     */
    public static Color darken(Color color, double factor) {
        return new Color(
            Math.max((int)(color.getRed() * (1 - factor)), 0),
            Math.max((int)(color.getGreen() * (1 - factor)), 0),
            Math.max((int)(color.getBlue() * (1 - factor)), 0),
            color.getAlpha()
        );
    }

    /**
     * Clareia uma cor
     */
    public static Color lighten(Color color, double factor) {
        return new Color(
            Math.min((int)(color.getRed() + (255 - color.getRed()) * factor), 255),
            Math.min((int)(color.getGreen() + (255 - color.getGreen()) * factor), 255),
            Math.min((int)(color.getBlue() + (255 - color.getBlue()) * factor), 255),
            color.getAlpha()
        );
    }

    /**
     * Converte Color para string hex
     */
    public static String toHex(Color color) {
        return String.format("#%02x%02x%02x", color.getRed(), color.getGreen(), color.getBlue());
    }
}

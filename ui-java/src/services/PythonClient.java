/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package services;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;

public class PythonClient {

    private static String chamarBackend(String rota) throws Exception {
        URL url = new URL("http://localhost:5000" + rota);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);

        conn.getOutputStream().write("{}".getBytes());

        BufferedReader br = new BufferedReader(
            new InputStreamReader(conn.getInputStream())
        );

        return br.readLine();
    }

    public static String calibrarCamera() throws Exception {
        return chamarBackend("/calibrar-camera");
    }

    public static String extrairFrames() throws Exception {
        return chamarBackend("/extrair-frames");
    }

    public static String reconstruir() throws Exception {
        return chamarBackend("/reconstruir");
    }

    public static String execucaoNormal() throws Exception {
        return chamarBackend("execucao-normal");
    }
    
    public static String historico() throws Exception {
        return chamarBackend("/historico");
    }
    

    // APENAS PARA TESTES FUTUROS DE HISTÓRICO
//     public static String historicoCalibracoes() throws Exception {
//         return chamarBackend("/historico-calibracoes");
//     }
//     public static String historicoFrames() throws Exception {
//         return chamarBackend("/historico-frames");
//     }
//     public static String historicoVideos() throws Exception {
//         return chamarBackend("/historico-videos");
//     }
//     public static String historicoVolumes() throws Exception {
//         return chamarBackend("/historico-volumes");
//     }
}

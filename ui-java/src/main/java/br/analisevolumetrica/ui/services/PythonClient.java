package br.analisevolumetrica.ui.services;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;

public class PythonClient {

    private static final String BASE_URL = "http://localhost:5000";
    
    private static String chamarGet(String rota) throws Exception {
        URL url = new URL(BASE_URL + rota);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        conn.setRequestMethod("GET");

        BufferedReader br = new BufferedReader(
            new InputStreamReader(
                conn.getResponseCode() >= 400
                    ? conn.getErrorStream()
                    : conn.getInputStream()
            )
        );

        StringBuilder resposta = new StringBuilder();
        String linha;
        while ((linha = br.readLine()) != null) {
            resposta.append(linha);
        }

        return resposta.toString();
    }
    
    private static String chamarPost(String rota) throws Exception {
        URL url = new URL(BASE_URL + rota);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);
        conn.getOutputStream().write("{}".getBytes());

        BufferedReader br = new BufferedReader(
            new InputStreamReader(
                conn.getResponseCode() >= 400
                    ? conn.getErrorStream()
                    : conn.getInputStream()
            )
        );

        StringBuilder resposta = new StringBuilder();
        String linha;
        while ((linha = br.readLine()) != null) {
            resposta.append(linha);
        }

        return resposta.toString();
    }

    public static String calibrarCamera() throws Exception {
        return chamarPost("/calibrar-camera");
    }

    public static String extrairFrames() throws Exception {
        return chamarPost("/extrair-frames");
    }

    public static String reconstruir() throws Exception {
        return chamarPost("/reconstruir");
    }

    public static String execucaoNormal() throws Exception {
        return chamarPost("/execucao-normal");
    }

    public static String calcularVolume() throws Exception {
        return chamarPost("/calcular-volume");
    }
    
    public static String historicoCalibracoes() throws Exception {
        return chamarGet("/historico-calibracoes");
    }
     
    public static String historicoFrames() throws Exception {
        return chamarGet("/historico-frames");
    }
     
    public static String historicoVideos() throws Exception {
        return chamarGet("/historico-videos");
    }
     
    public static String historicoVolumes() throws Exception {
        return chamarGet("/historico-volumes");
    }
     
    public static void encerrarServidor() {
        try {
            chamarPost("/shutdown");
        } catch (Exception e) {
            System.out.println("Aviso: Servidor Python já estava fechado ou não respondeu.");
        }
    }
}

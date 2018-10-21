package com.example.shaban.myapplication;

import android.app.ProgressDialog;
import android.content.Context;
import android.os.AsyncTask;

import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;
import com.mashape.unirest.http.exceptions.UnirestException;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;

public class CatalogQuery extends AsyncTask<String, Void, ArrayList<ArrayList<String>>> {

    private Context mContext;

    ProgressDialog mProgress;
    private TaskCompletedCatalog mCallback;

    public CatalogQuery(Context context){
        this.mContext = context;
        this.mCallback = (TaskCompletedCatalog) context;
    }

    @Override
    protected ArrayList<ArrayList<String>> doInBackground(String... queries) {
        try {
            URL url = new URL("https://gateway-staging.ncrcloud.com/catalog/items/snapshot");
            HttpURLConnection httpConn = (HttpURLConnection) url.openConnection();
            httpConn.setRequestMethod("GET");
            httpConn.setRequestProperty("accept", "application/json");
            httpConn.setRequestProperty("content-type", "application/json");
            httpConn.setRequestProperty("nep-application-key", "8a00860b6641a0ae016692b032bb0030");
            httpConn.setRequestProperty("Authorization", "Basic YWNjdDpmb29kaWVzQGZvb2RpZXNzZXJ2aWNldXNlcjpNaGFsbDEyMw==");
            httpConn.setRequestProperty("nep-organization", "ncr-market");
            httpConn.setRequestProperty("nep-service-version", "2.2.1:2");
            InputStream inputStream = httpConn.getInputStream();
            InputStreamReader inputStreamReader = new InputStreamReader(inputStream);
            BufferedReader bufferedReader = new BufferedReader(inputStreamReader);
            String line = bufferedReader.readLine();

            ArrayList<ArrayList<String>> entries = new ArrayList<>();
            JSONObject js = new JSONObject(line);
            for (int i = 0; i < js.getJSONArray("snapshot").length(); i++) {
                ArrayList<String> entry = new ArrayList<>(2);
                String code = js.getJSONArray("snapshot").getJSONObject(i)
                        .getJSONObject("itemId").getString("itemCode");
                entry.add(code);
                String name = js.getJSONArray("snapshot").getJSONObject(i)
                        .getJSONObject("longDescription").getJSONArray("values")
                        .getJSONObject(0).getString("value");
                entry.add(name);
                entries.add(entry);
            }
            return entries;
        } catch (JSONException e) {
            System.err.println(e.getStackTrace().toString());
        } catch (Exception e) {
            System.err.println(e.toString());
        }

        return null;
    }

    @Override
    protected void onPostExecute(ArrayList<ArrayList<String>> arrayList) {
        mCallback.onTaskComplete(arrayList);
    }
}

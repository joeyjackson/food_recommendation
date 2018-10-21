package com.example.shaban.myapplication;

import android.app.ProgressDialog;
import android.content.Context;
import android.graphics.Bitmap;
import android.os.AsyncTask;
import android.os.Environment;

import com.google.gson.JsonObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import org.json.*;

import clarifai2.api.ClarifaiBuilder;
import clarifai2.api.ClarifaiClient;
import clarifai2.api.ClarifaiResponse;
import clarifai2.dto.input.ClarifaiInput;
import okhttp3.OkHttpClient;

public class ClarifaiHelper extends AsyncTask<File, Void, ArrayList<String>> {

    private Context mContext;

    ProgressDialog mProgress;
    private TaskCompleted mCallback;

    public ClarifaiHelper(Context context){
        this.mContext = context;
        this.mCallback = (TaskCompleted) context;
    }

    @Override
    protected ArrayList<String> doInBackground(File... files) {
        ClarifaiClient client = new ClarifaiBuilder(
                "613085b28adc4d00a5464c4b473926d5").client(new OkHttpClient()).buildSync();


        ClarifaiResponse r = client.getDefaultModels().foodModel().predict()
                .withInputs(ClarifaiInput.forImage(files[0]))
                .executeSync();

        ArrayList<String> tags = new ArrayList<>(6);

        try {
            JSONObject js = new JSONObject(r.rawBody());
            for (int i = 0; i < 6; i++){
                JSONArray jsonArray = js.getJSONArray("outputs");
                System.out.println("SIZE OF THIS STUPID ARRAY: " + jsonArray.length());
                JSONObject jsonObject0 = (jsonArray.getJSONObject(0));
                JSONObject jsonObject01 = jsonObject0.getJSONObject("data");
                JSONArray jsonArray1 = jsonObject01.getJSONArray("concepts");
                JSONObject jsonObject1 = jsonArray1.getJSONObject(i);
                tags.add(i, jsonObject1.getString("name"));
                System.out.println("FINALLY FREAKING LOOPING! " + tags.get(i));
            }


        } catch (JSONException e) {
            System.err.println(e.getStackTrace());
        }

        System.out.println("TAGS: " + r.rawBody());
        return tags;
    }


    @Override
    protected void onPostExecute(ArrayList<String> arrayList) {
        mCallback.onTaskComplete(arrayList);
    }
}
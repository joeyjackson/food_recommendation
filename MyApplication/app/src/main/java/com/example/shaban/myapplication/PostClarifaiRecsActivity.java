package com.example.shaban.myapplication;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;

import java.util.ArrayList;
import java.util.List;

public class PostClarifaiRecsActivity extends AppCompatActivity implements TaskCompletedCatalog {

    ArrayList<String> validTags;
    RecyclerView rv;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_post_clarifai_recs);
        Intent intent = getIntent();
        validTags = (ArrayList<String>) intent.getExtras().get("tags");
        new CatalogQuery(this).execute(validTags.get(0));
    }

    @Override
    public void onTaskComplete(ArrayList<ArrayList<String>> result) {
        rv = (RecyclerView) findViewById(R.id.Cycle1);
        rv.setLayoutManager(new LinearLayoutManager(this));
        final ArrayList<String> names = new ArrayList<>();
        for (ArrayList<String> e : result) {
            names.add(e.get(1));
        }
        CatalogItemsAdapter ada = new CatalogItemsAdapter(PostClarifaiRecsActivity.this, names);

        rv.setAdapter(ada);
    }
}

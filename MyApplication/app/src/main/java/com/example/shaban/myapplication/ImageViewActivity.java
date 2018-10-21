package com.example.shaban.myapplication;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.ToggleButton;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;

public class ImageViewActivity extends AppCompatActivity implements TaskCompleted, View.OnClickListener{

    ToggleButton[] tagButtons;



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_image_view);
        tagButtons = new ToggleButton[]{findViewById(R.id.tag1), findViewById(R.id.tag2), findViewById(R.id.tag3), findViewById(R.id.tag4),findViewById((R.id.tag5)),findViewById(R.id.tag6)};
        System.out.println("got here three");
        Intent intent = getIntent();
        viewImage((Bitmap) intent.getExtras().get("bitmap"));
        System.out.println("I probably shall not print.");

        for (ToggleButton t : tagButtons) {
            t.setOnClickListener(this);
        }

        findViewById(R.id.confirmButton).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                ArrayList<String> validTags = new ArrayList<>();
                for (ToggleButton t : tagButtons) {
                    if (t.isChecked()) {
                        validTags.add(t.getText().toString());
                    }
                }
                if (validTags.size() == 0) {
                    return;
                }
                System.out.println(validTags.toString());
                openPostClarifaiRecs(validTags);
            }
        });
    }

    private void viewImage(Bitmap b) {
        ImageView mImageView = (ImageView)findViewById(R.id.imageView);
        mImageView.setImageBitmap(b);

        File f = convertBitMapToFile(b);
        new ClarifaiHelper(this).execute(f);
    }

    private File convertBitMapToFile(Bitmap bitmap) {
        File file = new File(getFilesDir(), "tempClarifaiFile.jpeg");
        System.out.println("image file should be created");

        try {
            FileOutputStream fOut = new FileOutputStream(file);

            bitmap.compress(Bitmap.CompressFormat.JPEG, 85, fOut);
            fOut.flush();
            fOut.close();
            System.out.println("bitmap has been pushed to fOut");
        } catch (IOException e) {
            System.err.println(e.toString());
            System.out.println("ERROR HAS BEEN CAUGHT IN TRY STATEMENT");
        }
        return file;
    }


    public void onTaskComplete(ArrayList<String> tags) {
        System.out.println("WE GOTS THE PRECIOUS" + tags.toString());

        for (int i = 0; i < 6; i++) {
            tagButtons[i].setText(tags.get(i));
            tagButtons[i].setTextOff(tags.get(i));
            tagButtons[i].setTextOn(tags.get(i));
            tagButtons[i].setBackgroundColor(Color.LTGRAY);
        }
    }

    @Override
    public void onClick(View v) {
        ToggleButton btn = (ToggleButton) v;
        if (btn.isChecked()){
            btn.setBackgroundColor(Color.GREEN);
        } else {
            btn.setBackgroundColor(Color.LTGRAY);
        }
    }

    private void openPostClarifaiRecs(ArrayList a) {
        Intent intent = new Intent(this, PostClarifaiRecsActivity.class);

        intent.putExtra("tags", a);

        startActivity(intent);

    }
}

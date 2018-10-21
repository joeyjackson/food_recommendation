package com.example.shaban.myapplication;

import android.content.Context;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

class CatalogItemsAdapter extends RecyclerView.Adapter<CatalogItemsAdapter.TextViewHolder>{
    private final List<String> in;
    private final LayoutInflater inflater;
    private SightingClickListener listener;

    CatalogItemsAdapter(Context context, List<String> in) {
        inflater = LayoutInflater.from(context);
        this.in = in;
    }

    @Override
    public TextViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View label = inflater.inflate(R.layout.catalog_entry, parent, false);
        return new TextViewHolder(label);
    }

    @Override
    public void onBindViewHolder(TextViewHolder holder, int position) {
        String str = in.get(position);
        holder.getView().setText(str);
    }

    @Override
    public int getItemCount() {
        return in.size();
    }


    void setClickListener(SightingClickListener listener) {
        this.listener = listener;
    }

    interface SightingClickListener {
        void onItemClick(int p);
    }

    public class TextViewHolder extends RecyclerView.ViewHolder implements View.OnClickListener {

        final TextView view;

        TextViewHolder(View itemView) {
            super(itemView);
            view = itemView.findViewById(R.id.Cycle1);
            itemView.setOnClickListener(this);
        }
        @Override
        public void onClick(View view) {
            if (listener != null) listener.onItemClick(getAdapterPosition());
        }

        public TextView getView() {
            return view;
        }
    }
}
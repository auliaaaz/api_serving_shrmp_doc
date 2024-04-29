from flask import Flask, request, jsonify
import logging
import joblib
import pandas as pd
import sqlite3

app = Flask(__name__)

# Load models
sr_waterbased_model = joblib.load("survival_rate_random_forest_water_based2.joblib")
sr_feedbased_model = joblib.load("survival_rate_random_forest.joblib")
abw_model = joblib.load("ABW_random_forest.joblib")

sr_waterbased_features = [
    "total_seed", "area", "pond_depth", "total_cult_days",  
    "morning_temperature", "evening_temperature", "morning_do", "evening_do", "morning_salinity", "evening_salinity",
    "morning_pH", "evening_pH", "transparency", "day_of_cult"
]

sr_feedbased_features = [
    "total_seed", "area", "pond_depth", "total_cult_days",  
    "quantity_avg_daily", "day_of_cult", "feed_per_unit_area", "feed_per_cult_day"
    
]

abw_features = [
    "quantity_perday_freq", "quantity_avg_daily", "total_seed", "area", 
    "pond_depth", "total_cult_days", "day_of_cult", "feed_per_unit_area", "feed_per_cult_day"
]

def price_est(avg_body_weight):
    size = 1000 / avg_body_weight
    if size <= 40:
        return 94000
    elif 40 < size <= 70:
        return 73000
    elif 70 < size <= 100:
        return 56000
    else:
        return 40000

# create functions to create database to store feature values and prediction values
def create_database():
    conn = sqlite3.connect('feature_store.db')

    # Create a table for storing features
    feature_table_schema = """
    CREATE TABLE IF NOT EXISTS all_features (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day_of_cult INTEGER,
        total_seed INTEGER,
        total_cult_days INTEGER,
        area FLOAT,
        pond_depth FLOAT,
        feed_per_unit_area FLOAT,
        feed_per_cult_day FLOAT,
        quantity_avg_daily FLOAT,
        quantity_perday_freq INTEGER,
        morning_temperature FLOAT,
        evening_temperature FLOAT,
        morning_do FLOAT,
        evening_do FLOAT,
        morning_pH FLOAT,
        evening_pH FLOAT,
        morning_salinity FLOAT,
        evening_salinity FLOAT,
        transparency FLOAT
    )
    """
    conn.execute(feature_table_schema)

    prediction_table_schema = """
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feature_id INTEGER, 
        sr_prediction FLOAT,
        abw_prediction FLOAT,
        biomass_prediction FLOAT,
        revenue_prediction FLOAT,
        created_at TIMESTAMP,
        FOREIGN KEY (feature_id) REFERENCES all_features(id) 
    )
    """
    conn.execute(prediction_table_schema)
    conn.close()
    
create_database()

@app.route('/predict/all', methods=['POST'])
def predict_all():
    try:
        input_data = request.json
        
        # connect to sqlite
        conn = sqlite3.connect('feature_store.db')
        
        input_df = pd.DataFrame([input_data])
        
        # store features to sqlite
        input_df.to_sql('all_features', conn, if_exists='append', index=False)
        feature_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        waterbased_input = input_df[sr_waterbased_features]
        feedbased_input = input_df[sr_feedbased_features]
        abw_input = input_df[abw_features]

        # prediction model
        feed_prediction = sr_feedbased_model.predict(feedbased_input)[0]
        water_quality_prediction = sr_waterbased_model.predict(waterbased_input)[0]
        abw_prediction = abw_model.predict(abw_input)[0]

        # data validation
        if not all(isinstance(val, (int, float)) for val in [feed_prediction, water_quality_prediction, abw_prediction]):
            raise ValueError("Model predictions must return numeric values.")

        # calculate survival rate prediction
        survival_rate_prediction = (feed_prediction + water_quality_prediction) / 2
        
        # biomass prediction and revenue
        biomass_prediction = survival_rate_prediction * abw_prediction
        price = price_est(abw_prediction)
        revenue_prediction = biomass_prediction * price

        # store predictions
        prediction_data_all = {"feature_id": feature_id,
                               "sr_prediction": survival_rate_prediction,
                               "abw_prediction": abw_prediction,
                               "biomass_prediction": biomass_prediction,
                               "revenue_prediction": revenue_prediction
                               } 
        
        predictions_df = pd.DataFrame([prediction_data_all])
        predictions_df.to_sql('predictions', conn, if_exists='append', index=False)
        
        conn.close()
        
        return jsonify({
            "survival_rate_prediction": survival_rate_prediction,
            "avg_body_weight_prediction": abw_prediction,
            "biomass_prediction": biomass_prediction,
            "revenue_prediction": revenue_prediction
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)    

    

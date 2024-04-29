# API Documentation for Prediction Service
This Flask-based API provides a predictive service for aquaculture data. It allows users to submit feature data and receive predictions for survival rate, average body weight (ABW), biomass, and revenue.

## Models
Three pre-trained models are used to generate predictions:
1. sr_waterbased_model: Predicts water-based survival rate.
2. sr_feedbased_model: Predicts feed-based survival rate.
3. abw_model: Predicts average body weight (ABW).
The models can be accessed through [this drive link](https://drive.google.com/file/d/1Kf4Kkp7SL9NrF2-L6gpc2FUosmAj9_Lv/view?usp=sharing)

## Endpoints
The API exposes the following endpoint:

`/predict/all`

Method: POST

Description: Predicts survival rate, average body weight, biomass, and revenue based on provided input data.

Request Format: JSON

Response Format: JSON

Request Body Parameters:
  The request should contain a JSON object with the following fields:
  1. `total_seed`: Number of seeds in the pond (Integer)
  2. `area`: Area of the pond (Float)
  3. `pond_depth`: Depth of the pond (Float)
  4. `total_cult_days`: Total culture days (Integer)
  5. `morning_temperature`: Temperature in the morning (Float)
  6. `evening_temperature`: Temperature in the evening (Float)
  7. `morning_do`: Dissolved oxygen levels in the morning (Float)
  8. `evening_do`: Dissolved oxygen levels in the evening (Float)
  9. `morning_pH`: pH levels in the morning (Float)
  10. `evening_pH`: pH levels in the evening (Float)
  11. `morning_salinity`: Salinity levels in the morning (Float)
  12. `evening_salinity`: Salinity levels in the evening (Float)
  13. `transparency`: Transparency of the pond (Float)
  14. `day_of_cult`: Day of culture (Integer)
  15. `quantity_avg_daily`: Average daily feed quantity (Float)
  16. `quantity_perday_freq`: Frequency of feed per day (Integer)
  17. `feed_per_unit_area`: Feed per unit area (Float)
  18. `feed_per_cult_day`: Feed per culture day (Float)

Response Body:

  If the prediction is successful, a JSON object containing:
  
  1. `survival_rate_prediction`: Predicted survival rate (Float)
  2. `avg_body_weight_prediction`: Predicted average body weight (Float)
  3. `biomass_prediction`: Predicted biomass (Float)
  4. `revenue_prediction`: Predicted revenue (Float)
  
Error Handling:
If an error occurs during prediction, a JSON object with an "error" key containing the error message will be returned

Sample Request:
```
  {
  "day_of_cult": 60,
  "total_seed": 125000,
  "total_cult_days": 70,
  "area": 4001,
  "pond_depth": 1.2,
  "feed_per_unit_area": 0.02,
  "feed_per_cult_day": 0.5,
  "quantity_avg_daily": 150,
  "quantity_perday_freq": 2,
  "morning_temperature": 25,
  "evening_temperature": 20,
  "morning_do": 6.5,
  "evening_do": 8.5,
  "morning_pH": 8,
  "evening_pH": 9.5,
  "morning_salinity": 13,
  "evening_salinity": 13.6,
  "transparency": 77
}
```
Sample Response:
```
{
    "avg_body_weight_prediction": 9.649290322580644,
    "biomass_prediction": 464.80998156903274,
    "revenue_prediction": 18592399.26276131,
    "survival_rate_prediction": 48.17038000000006
}
```

## Database
The API uses SQLite to store feature data and predictions:

Feature Store:

  Table all_features: Stores the input features used for predictions.
  
  Fields: id, day_of_cult, total_seed, total_cult_days, area, pond_depth, feed_per_unit_area, feed_per_cult_day, quantity_avg_daily, quantity_perday_freq, morning_temperature, evening_temperature, morning_do, evening_do, morning_pH,   evening_pH, morning_salinity, evening_salinity, transparency.
  
Prediction Store:

  Table predictions: Stores the predictions based on the features.
  
  Fields: id, feature_id, sr_prediction, abw_prediction, biomass_prediction, revenue_prediction, created_at.

## Running the Service
Before running the service, ensure that Python and SQLite3 are installed on your system. To set up a virtual environment and install the required packages, follow these steps:
1. Create virtual environment
   ```
   python -m venv myenv
   ```
2. Activate the Virtual Environment
   * On windows
    ```
    myenv\Scripts\activate
    ```
   * On Linux/macOS
    ```
    source myenv/bin/activate
    ```

3. Install the Required Packages
   
    With the virtual environment activated, install the packages listed in `requirements.txt`:
    ```
    pip install -r requirements.txt
    ```

4. Run the Application with
    ```
    python app.py
    ```

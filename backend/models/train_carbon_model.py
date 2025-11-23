import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pickle
import numpy as np

def train_xgboost_co2_model():
    """
    Train XGBoost model to predict CO2 emissions
    
    Goal: Create CO2 scores for each model that will be used by the 
    recommendation algorithm to suggest the most efficient model for a task
    
    Input Features:
    - inference_speed_tokens_sec (primary driver)
    - datacenter_count (secondary factor)
    
    Output:
    - co2_grams_per_request (prediction target)
    
    The trained model will be used to:
    1. Predict CO2 for all 50 models
    2. Rank models by efficiency
    3. Recommend lowest CO2 option for each task type
    """
    
    print("=" * 70)
    print("TRAINING CO2 EMISSION PREDICTION MODEL")
    print("=" * 70)
    
    # ========== STEP 1: LOAD DATA ==========
    print("\ntep 1: Loading training data...")
    df = pd.read_csv('../data/llm_models_training.csv')
    
    print(f"   ✓ Loaded {len(df)} models")
    print(f"   ✓ Columns: {list(df.columns)}")
    
    # ========== STEP 2: PREPARE FEATURES ==========
    print("\nStep 2: Preparing features...")
    
    # Define input features (X)
    feature_cols = ['inference_speed_tokens_sec', 'datacenter_count']
    X = df[feature_cols].copy()
    
    # Define target variable (y) - what we want to predict
    y = df['co2_grams_per_request'].copy()
    
    print(f"Features (X): {feature_cols}")
    print(f"Target (y): co2_grams_per_request")
    print(f"\n   Feature Statistics:")
    print(X.describe())
    print(f"\n   Target Statistics (CO2 in grams):")
    print(y.describe())
    
    # ========== STEP 3: SPLIT DATA ==========
    print("\nStep 3: Splitting data...")
    
    # Split: 80% training, 20% testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2,      # 20% for testing
        random_state=42,    # Reproducible results
        shuffle=True
    )
    
    print(f"   ✓ Training set: {len(X_train)} samples ({len(X_train)/len(X)*100:.0f}%)")
    print(f"   ✓ Test set: {len(X_test)} samples ({len(X_test)/len(X)*100:.0f}%)")
    
    # ========== STEP 4: TRAIN XGBOOST MODEL ==========
    print("\nStep 4: Training XGBoost model...")
    
    # Configure XGBoost
    model = xgb.XGBRegressor(
        # Core parameters
        n_estimators=150,           # Number of trees (more = better fit, but slower)
        max_depth=5,                # Maximum tree depth (prevents overfitting)
        learning_rate=0.08,         # Step size (lower = more careful learning)
        
        # Regularization (prevents overfitting)
        subsample=0.8,              # Use 80% of data for each tree
        colsample_bytree=0.8,       # Use 80% of features for each tree
        reg_alpha=0.1,              # L1 regularization
        reg_lambda=1.0,             # L2 regularization
        
        # Other settings
        random_state=42,
        objective='reg:squarederror',  # Regression task
        n_jobs=-1                   # Use all CPU cores
    )
    
    # Train the model
    model.fit(
        X_train, y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        verbose=False
    )
    
    print("Training complete!")
    
    # ========== STEP 5: EVALUATE MODEL ==========
    print("\nStep 5: Evaluating model performance...")
    
    # Make predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Calculate metrics
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    test_mae = mean_absolute_error(y_test, y_pred_test)
    
    print(f"\n   Performance Metrics:")
    print(f"   ├─ Training R²:    {train_r2:.4f}  (1.0 = perfect)")
    print(f"   ├─ Test R²:        {test_r2:.4f}  (higher = better)")
    print(f"   ├─ Training RMSE:  {train_rmse:.4f}g CO2")
    print(f"   ├─ Test RMSE:      {test_rmse:.4f}g CO2  (lower = better)")
    print(f"   └─ Test MAE:       {test_mae:.4f}g CO2  (average error)")
    
    # Interpretation
    if test_r2 > 0.85:
        print(f"\n Excellent model! R² > 0.85")
    elif test_r2 > 0.70:
        print(f"\n Good model! R² > 0.70")
    else:
        print(f"\n  Model needs improvement (R² < 0.70)")
    
    # ========== STEP 6: FEATURE IMPORTANCE ==========
    print("\nStep 6: Analyzing feature importance...")
    
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n   Feature Importance (which matters most?):")
    for idx, row in feature_importance.iterrows():
        bar_length = int(row['importance'] * 50)
        bar = '█' * bar_length
        print(f"   {row['feature']:30s} {bar} {row['importance']:.4f}")
    
    # ========== STEP 7: PREDICT CO2 FOR ALL MODELS ==========
    print("\nStep 7: Generating CO2 scores for all models...")
    
    # Predict for entire dataset
    df['co2_predicted'] = model.predict(X)
    df['prediction_error'] = abs(df['co2_grams_per_request'] - df['co2_predicted'])
    
    # Add efficiency ranking (1 = most efficient)
    df['efficiency_rank'] = df['co2_predicted'].rank(method='min').astype(int)
    
    print(f"   ✓ Generated CO2 predictions for all {len(df)} models")
    
    # Show efficiency rankings
    print("\n  Top 5 Most Efficient Models (Lowest CO2):")
    top5 = df.nsmallest(5, 'co2_predicted')[
        ['Model', 'inference_speed_tokens_sec', 'co2_predicted', 'efficiency_rank']
    ]
    print(top5.to_string(index=False))
    
    print("\nTop 5 Least Efficient Models (Highest CO2):")
    bottom5 = df.nlargest(5, 'co2_predicted')[
        ['Model', 'inference_speed_tokens_sec', 'co2_predicted', 'efficiency_rank']
    ]
    print(bottom5.to_string(index=False))
    
    # ========== STEP 8: SAVE MODEL ==========
    # Save the XGBoost model
    with open('energy_predictor.pkl', 'wb') as f:
        pickle.dump(model, f)
    print(f"   ✓ Model saved: backend/models/energy_predictor.pkl")
    
    # Save feature names (for later predictions)
    model_metadata = {
        'feature_names': feature_cols,
        'model_type': 'XGBRegressor',
        'test_r2': float(test_r2),
        'test_rmse': float(test_rmse),
        'training_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        'n_models': len(df)
    }
    
    with open('model_metadata.json', 'w') as f:
        import json
        json.dump(model_metadata, f, indent=2)
    print(f"   ✓ Metadata saved: backend/models/model_metadata.json")
    
    # ========== STEP 9: SAVE FINAL DATASET ==========    
    # Save complete dataset with predictions
    output_cols = [
        'Model',
        'Overall',
        'company',
        'inference_speed_tokens_sec',
        'datacenter_count',
        'co2_grams_per_request',      # Actual (from calculation)
        'co2_predicted',               # Predicted (from XGBoost)
        'efficiency_rank'              # Ranking (1 = best)
    ]
    
    df_final = df[output_cols].copy()
    df_final.to_csv('../data/llm_models_final.csv', index=False)
    
    print(f"   ✓ Final dataset saved: backend/data/llm_models_final.csv")
    print(f"   ✓ Ready for recommendation algorithm!")
    
    # ========== STEP 10: SUMMARY ==========
    print("\n" + "=" * 70)
    print("CO2 PREDICTION MODEL TRAINING COMPLETE!")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"   • Models analyzed: {len(df)}")
    print(f"   • Test R² score: {test_r2:.4f}")
    print(f"   • Average prediction error: {test_mae:.4f}g CO2")
    print(f"   • Most important feature: {feature_importance.iloc[0]['feature']}")
    
    return model, df_final

if __name__ == "__main__":
    model, df = train_xgboost_co2_model()
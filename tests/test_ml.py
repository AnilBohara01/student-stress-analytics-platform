import os
import sys
import unittest
import pandas as pd
import numpy as np

# Ensure ml/src is in system path for standalone ML testing
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml', 'src'))

from preprocessing import load_and_clean_data, build_preprocessing_pipeline, split_data
from predict import predict_stress, load_model_pipeline
from explain import explain_prediction


class MLPipelineTestCase(unittest.TestCase):
    def setUp(self):
        self.data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ml', 'data', 'StressLevelDataset.csv'
        )
        self.sample_student = {
            "Student_Type": "college",
            "Sleep_Hours": 6.0,
            "Study_Hours": 7.5,
            "Social_Media_Hours": 3.0,
            "Attendance": 80.0,
            "Exam_Pressure": 7.5,
            "Family_Support": 5.0,
            "Month": 9.0
        }

    def test_load_and_clean_data(self):
        df = load_and_clean_data(self.data_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.duplicated().sum(), 0)
        self.assertIn('Stress_Level', df.columns)

    def test_preprocessing_pipeline_transformation(self):
        df = load_and_clean_data(self.data_path)
        X_train, X_test, y_train, y_test = split_data(df, test_size=0.2, random_state=42)
        
        preprocessor = build_preprocessing_pipeline()
        X_train_trans = preprocessor.fit_transform(X_train)
        X_test_trans = preprocessor.transform(X_test)

        self.assertEqual(X_train_trans.shape[1], 9)  # 7 numerical + 2 OneHot categorical
        self.assertEqual(X_test_trans.shape[1], 9)
        self.assertFalse(np.isnan(X_train_trans).any())
        self.assertFalse(np.isnan(X_test_trans).any())

    def test_predict_stress_inference(self):
        result = predict_stress(self.sample_student)
        self.assertIn(result['prediction_code'], [0, 1])
        self.assertIn(result['predicted_label'], ["Low/Normal Stress", "High Stress"])
        
        probs = result['probabilities']
        self.assertGreaterEqual(probs['low_normal_stress'], 0.0)
        self.assertLessEqual(probs['low_normal_stress'], 1.0)
        self.assertGreaterEqual(probs['high_stress'], 0.0)
        self.assertLessEqual(probs['high_stress'], 1.0)
        self.assertAlmostEqual(probs['low_normal_stress'] + probs['high_stress'], 1.0, places=3)
        self.assertEqual(result['model_version'], "stresslens_v1.0.0")

    def test_explain_prediction_shap(self):
        explanation = explain_prediction(self.sample_student)
        self.assertIn('top_contributing_factors', explanation)
        self.assertIn('narrative_explanation', explanation)
        
        factors = explanation['top_contributing_factors']
        self.assertGreater(len(factors), 0)
        for factor in factors:
            self.assertIn('feature_label', factor)
            self.assertIn('shap_value', factor)
            self.assertIn('impact_direction', factor)


if __name__ == '__main__':
    unittest.main()

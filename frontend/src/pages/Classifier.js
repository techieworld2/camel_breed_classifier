import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import { predictionAPI, featureAPI } from '../api';
import { toast } from 'react-toastify';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import './Classifier.css';

export const Classifier = () => {
  const { user, logout } = useAuth();
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [facts, setFacts] = useState([]);
  const [loadingFacts, setLoadingFacts] = useState(false);

  // Tabular features - matching your Streamlit app
  const [headSize, setHeadSize] = useState(3.0);
  const [legCondition, setLegCondition] = useState(3.0);
  const [coatQuality, setCoatQuality] = useState(3.0);
  const [overallFitness, setOverallFitness] = useState(3.0);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.60);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
      setResult(null);
      setFacts([]);
    }
  };

  const handleClassify = async () => {
    if (!image) {
      toast.error('Please select an image first');
      return;
    }

    setLoading(true);
    setResult(null);
    setFacts([]);

    try {
      const formData = new FormData();
      formData.append('file', image);
      formData.append('head_size', headSize);
      formData.append('leg_condition', legCondition);
      formData.append('coat_quality', coatQuality);
      formData.append('overall_fitness', overallFitness);
      formData.append('confidence_threshold', confidenceThreshold);

      const response = await predictionAPI.classify(formData);
      setResult(response.data);
      
      // Load facts for the predicted breed
      if (response.data.breed) {
        setLoadingFacts(true);
        try {
          const factsResponse = await featureAPI.getBreedFacts(response.data.breed);
          setFacts(factsResponse.data.facts || []);
          if (factsResponse.data.error) {
            console.error('Gemini API Error:', factsResponse.data.error);
            toast.warning(`Facts unavailable: ${factsResponse.data.error}`);
          }
        } catch (error) {
          console.error('Failed to load facts:', error);
        } finally {
          setLoadingFacts(false);
        }
      }

      toast.success('Classification successful!');
    } catch (error) {
      const message = error.response?.data?.detail || 'Classification failed';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setImage(null);
    setPreview(null);
    setResult(null);
    setFacts([]);
    setHeadSize(3.0);
    setLegCondition(3.0);
    setCoatQuality(3.0);
    setOverallFitness(3.0);
    setConfidenceThreshold(0.60);
  };

  // Prepare data for bar chart
  const chartData = result?.probabilities
    ? Object.entries(result.probabilities).map(([breed, confidence]) => ({
        breed: breed.replace(' Camel', ''),
        confidence: (confidence * 100).toFixed(1),
        confidenceValue: confidence * 100,
      }))
    : [];

  const COLORS = ['#667eea', '#764ba2', '#f093fb'];

  return (
    <div className="classifier-container">
      <header className="classifier-header">
        <h1>🐪 Camel Breed Classifier</h1>
        <div className="user-section">
          <span>Welcome, {user?.username}!</span>
          <button onClick={logout} className="btn btn-secondary">Logout</button>
        </div>
      </header>

      <div className="classifier-content">
        <div className="left-panel">
          {/* Image Upload Section */}
          <div className="upload-section">
            <h2>Upload Camel Image</h2>
            <div className="image-upload">
              <label htmlFor="image-input" className="upload-label">
                {preview ? (
                  <img src={preview} alt="Preview" className="preview-image" />
                ) : (
                  <div className="upload-placeholder">
                    <span className="upload-icon">📷</span>
                    <p>Click to upload camel image</p>
                  </div>
                )}
              </label>
              <input
                id="image-input"
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="file-input"
              />
            </div>
          </div>

          {/* Tabular Features Section */}
          <div className="features-section">
            <h2>Camel Features (0.0 - 5.0)</h2>
            <p className="features-subtitle">Adjust traits: 0 = poor, 5 = excellent</p>
            
            <div className="feature-input">
              <label>
                Head Size: <strong>{headSize.toFixed(1)}</strong>
              </label>
              <input
                type="range"
                min="0"
                max="5"
                step="0.1"
                value={headSize}
                onChange={(e) => setHeadSize(parseFloat(e.target.value))}
                className="slider"
              />
            </div>

            <div className="feature-input">
              <label>
                Leg Condition: <strong>{legCondition.toFixed(1)}</strong>
              </label>
              <input
                type="range"
                min="0"
                max="5"
                step="0.1"
                value={legCondition}
                onChange={(e) => setLegCondition(parseFloat(e.target.value))}
                className="slider"
              />
            </div>

            <div className="feature-input">
              <label>
                Coat Quality: <strong>{coatQuality.toFixed(1)}</strong>
              </label>
              <input
                type="range"
                min="0"
                max="5"
                step="0.1"
                value={coatQuality}
                onChange={(e) => setCoatQuality(parseFloat(e.target.value))}
                className="slider"
              />
            </div>

            <div className="feature-input">
              <label>
                Overall Fitness: <strong>{overallFitness.toFixed(1)}</strong>
              </label>
              <input
                type="range"
                min="0"
                max="5"
                step="0.1"
                value={overallFitness}
                onChange={(e) => setOverallFitness(parseFloat(e.target.value))}
                className="slider"
              />
            </div>

            <div className="feature-input">
              <label>
                Confidence Threshold: <strong>{confidenceThreshold.toFixed(2)}</strong>
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
                className="slider"
              />
            </div>
          </div>

          <div className="button-group">
            <button
              onClick={handleClassify}
              disabled={!image || loading}
              className="btn btn-primary"
            >
              {loading ? 'Classifying...' : 'Classify'}
            </button>
            <button
              onClick={handleReset}
              disabled={!image}
              className="btn btn-secondary"
            >
              Reset
            </button>
          </div>
        </div>

        {/* Results Panel */}
        <div className="right-panel">
          {result && (
            <>
              {/* Prediction Result */}
              <div className="result-card">
                <h2>Prediction: {result.breed}</h2>
                <div className="metrics">
                  <div className="metric">
                    <span className="metric-label">Breed</span>
                    <span className="metric-value breed">{result.breed}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Confidence</span>
                    <span className="metric-value confidence">
                      {(result.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Rating</span>
                    <span className="metric-value rating">{result.rating.toFixed(2)}</span>
                  </div>
                </div>
                {result.is_dromedary_fallback && (
                  <p className="fallback-notice">
                    ⚠️ Low confidence: Showing general Dromedary classification
                  </p>
                )}
              </div>

              {/* Probability Bar Chart */}
              <div className="result-card">
                <h2>Class Probabilities</h2>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="breed" 
                      angle={-45} 
                      textAnchor="end" 
                      height={80}
                      style={{ fontSize: '12px' }}
                    />
                    <YAxis 
                      label={{ value: 'Confidence (%)', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip 
                      formatter={(value) => `${value}%`}
                      contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
                    />
                    <Bar dataKey="confidenceValue" name="Confidence">
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Grad-CAM Visualization */}
              {result.gradcam_image && (
                <div className="result-card">
                  <h2>Grad-CAM Visualization</h2>
                  <img 
                    src={`data:image/png;base64,${result.gradcam_image}`}
                    alt="Grad-CAM" 
                    className="gradcam-image" 
                  />
                  <p className="gradcam-info">
                    Red/yellow regions show which parts influenced the classification
                  </p>
                </div>
              )}

              {/* Breed Facts */}
              <div className="result-card">
                <h2>10 Facts about: {result.breed}</h2>
                {loadingFacts ? (
                  <p>Loading facts from Gemini AI...</p>
                ) : facts.length > 0 ? (
                  <ul className="facts-list">
                    {facts.map((fact, index) => (
                      <li key={index}>{fact}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="no-facts">Facts not available</p>
                )}
              </div>
            </>
          )}

          {!result && (
            <div className="empty-state">
              <p>👈 Upload an image and adjust features to get started</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

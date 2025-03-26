import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ConvertibleBondsBacktest.css';
import api from '../utils/axios';

export default function ConvertibleBondsBacktest() {
  const COMPARATORS = ['<', '>', '==', '<=', '>='];

  // Initial state with values
  const initialState = {
    data: {
      cb_data_path: '',
      index_data_path: '',
      start_date: '2022-08-01',
      end_date: '2025-12-31'
    },
    strategy: {
      exclude_conditions: {
        price: {
          enabled: true,
          conditions: [
            { comparator: '<', value: 102 },
            { comparator: '>', value: 155 }
          ]
        },
        duration: {
          enabled: true,
          conditions: [
            { comparator: '<', value: 0.7 }
          ]
        },
        volume: {
          enabled: true,
          conditions: [
            { comparator: '<', value: 1000 }
          ]
        }
      },
      score_factors: ['bond_prem', 'ytm', 'turnover_5'],
      weights: [-10, 10, 5],
      hold_num: 5,
      stop_profit: 0.03,
      fee_rate: 0.002
    }
  };

  // Empty state for reset - keep score_factors structure
  const emptyState = {
    data: {
      cb_data_path: '',
      index_data_path: '',
      start_date: '',
      end_date: ''
    },
    strategy: {
      exclude_conditions: {
        price: {
          enabled: false,
          conditions: [
            { comparator: '', value: '' }
          ]
        },
        duration: {
          enabled: false,
          conditions: [
            { comparator: '', value: '' }
          ]
        },
        volume: {
          enabled: false,
          conditions: [
            { comparator: '', value: '' }
          ]
        }
      },
      score_factors: ['bond_prem', 'ytm', 'turnover_5'],
      weights: [0, 0, 0],
      hold_num: '',
      stop_profit: '',
      fee_rate: ''
    }
  };

  // States
  const [data, setData] = useState(initialState.data);
  const [strategy, setStrategy] = useState(initialState.strategy);
  const [jsonOutput, setJsonOutput] = useState(null);
  const [error, setError] = useState(null);
  const [backtestResults, setBacktestResults] = useState(null);

  // Add state for loading
  const [isLoading, setIsLoading] = useState(true);

  // Add navigate
  const navigate = useNavigate();
  
  // Update the useEffect to handle loading state
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }
        
        // Verify token with backend if needed
        // const response = await api.get('/api/verify-token');
        
        setIsLoading(false); // Set loading to false after auth check
      } catch (error) {
        console.error('Auth check error:', error);
        localStorage.removeItem('token');
        navigate('/login');
      }
    };

    checkAuth();
  }, [navigate]);

  // Add early return for loading state
  if (isLoading) {
    return <div>Loading...</div>;
  }

  // Reset handler - make sure to set jsonOutput to null
  const handleReset = () => {
    setData(emptyState.data);
    setStrategy({
      ...emptyState.strategy,
      score_factors: strategy.score_factors,
      weights: strategy.score_factors.map(() => 0)
    });
    setJsonOutput(null); // This will remove the Generated Configuration box
    console.log('Reset clicked, all values cleared and output removed');
  };

  // Date format conversion functions
  const getStorageFormat = (dateStr) => {
    return dateStr.replace(/-/g, '');
  };

  // Update handleGenerateConfig to include error handling
  const handleGenerateConfig = async () => {
    try {
      setError(null);
      const configData = {
        data: {
          ...data,
          start_date: data.start_date ? getStorageFormat(data.start_date) : '',
          end_date: data.end_date ? getStorageFormat(data.end_date) : ''
        },
        strategies: [strategy],
        output_path: 'result/backtest_output.xlsx'
      };

      const response = await api.post('/api/backtest', configData);
      
      if (response.data.status === 'success') {
        setJsonOutput(configData);
        setBacktestResults(response.data.performance);
      } else {
        throw new Error(response.data.message || 'Failed to generate config');
      }
    } catch (error) {
      console.error('Error generating config:', error);
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
        return;
      }
      setError(error.message || 'Error generating configuration');
    }
  };

  // Handler for date changes
  const handleDateChange = (field) => (event) => {
    const newDate = event.target.value; // Already in yyyy-MM-dd format
    setData(prev => ({
      ...prev,
      [field]: newDate
    }));
  };

  // Get the storage format (yyyyMMdd) for display and API
  const getDisplayFormat = (dateStr) => {
    return dateStr.replace(/-/g, '');
  };

  // Handler for data section updates
  const handleDataChange = (field, value) => {
    setData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handler for strategy updates
  const handleStrategyChange = (field, value) => {
    setStrategy(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handler for exclude condition changes
  const handleExcludeConditionChange = (category, field, value) => {
    setStrategy(prev => ({
      ...prev,
      exclude_conditions: {
        ...prev.exclude_conditions,
        [category]: {
          ...prev.exclude_conditions[category],
          [field]: field === 'enabled' ? value : Number(value)
        }
      }
    }));
  };

  // Handler for condition changes
  const handleConditionChange = (category, index, field, value) => {
    setStrategy(prev => ({
      ...prev,
      exclude_conditions: {
        ...prev.exclude_conditions,
        [category]: {
          ...prev.exclude_conditions[category],
          conditions: prev.exclude_conditions[category].conditions.map((condition, i) => 
            i === index 
              ? { ...condition, [field]: field === 'value' ? Number(value) : value }
              : condition
          )
        }
      }
    }));
  };

  // Handler for adding new conditions
  const addCondition = (category) => {
    setStrategy(prev => ({
      ...prev,
      exclude_conditions: {
        ...prev.exclude_conditions,
        [category]: {
          ...prev.exclude_conditions[category],
          conditions: [
            ...prev.exclude_conditions[category].conditions,
            { comparator: '<', value: 0 }
          ]
        }
      }
    }));
  };

  // Handler for removing conditions
  const removeCondition = (category, index) => {
    setStrategy(prev => ({
      ...prev,
      exclude_conditions: {
        ...prev.exclude_conditions,
        [category]: {
          ...prev.exclude_conditions[category],
          conditions: prev.exclude_conditions[category].conditions.filter((_, i) => i !== index)
        }
      }
    }));
  };

  // Function to generate condition strings for API
  const generateConditionStrings = () => {
    const conditions = [];
    Object.entries(strategy.exclude_conditions).forEach(([category, data]) => {
      if (data.enabled) {
        data.conditions.forEach(condition => {
          const field = category === 'price' ? 'close' 
                     : category === 'duration' ? 'left_years'
                     : 'amount';
          conditions.push(`${field} ${condition.comparator} ${condition.value}`);
        });
      }
    });
    return conditions;
  };

  // Update handleLogout to properly clean up
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    navigate('/login');
  };

  return (
    <div className="backtest-container">
      {error && <div className="error-message">{error}</div>}
      <div className="header">
        <h1>Convertible Bond Backtesting</h1>
        <div className="user-controls">
          <span>Welcome, {localStorage.getItem('username')}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
      
      <form onSubmit={(e) => {
        e.preventDefault();
        const config = {
          data,
          strategies: [{
            ...strategy,
            exclude_conditions: generateConditionStrings()
          }],
          output_path: 'result/backtest_output.xlsx'
        };
        
        // Update the JSON output state
        setJsonOutput(config);
      }}>
        {/* Data Section */}
        <section className="config-section">
          <h2>Data Configuration</h2>
          <div className="section-content">
            <div className="input-group">
              <label>Start Date:</label>
              <input
                type="date"
                value={data.start_date}
                onChange={(e) => setData(prev => ({
                  ...prev,
                  start_date: e.target.value
                }))}
              />
              <span className="date-value">
                {data.start_date && `yyyyMMdd: ${getStorageFormat(data.start_date)}`}
              </span>
            </div>
            <div className="input-group">
              <label>End Date:</label>
              <input
                type="date"
                value={data.end_date}
                onChange={(e) => setData(prev => ({
                  ...prev,
                  end_date: e.target.value
                }))}
              />
              <span className="date-value">
                {data.end_date && `yyyyMMdd: ${getStorageFormat(data.end_date)}`}
              </span>
            </div>
          </div>
        </section>

        {/* Updated Exclude Conditions Section */}
        <section className="config-section">
          <h2>Exclude Conditions</h2>
          
          {/* Price Conditions */}
          <div className="condition-category">
            <div className="condition-header">
              <label className="condition-checkbox">
                <input
                  type="checkbox"
                  checked={strategy.exclude_conditions.price.enabled}
                  onChange={(e) => handleExcludeConditionChange('price', 'enabled', e.target.checked)}
                />
                <h3>Price Conditions</h3>
              </label>
            </div>
            
            {strategy.exclude_conditions.price.enabled && (
              <div className="condition-inputs">
                {strategy.exclude_conditions.price.conditions.map((condition, index) => (
                  <div key={index} className="condition-row">
                    <select
                      value={condition.comparator}
                      onChange={(e) => handleConditionChange('price', index, 'comparator', e.target.value)}
                      className="comparator-select"
                    >
                      {COMPARATORS.map(comp => (
                        <option key={comp} value={comp}>{comp}</option>
                      ))}
                    </select>
                    <input
                      type="number"
                      value={condition.value}
                      onChange={(e) => handleConditionChange('price', index, 'value', e.target.value)}
                      step="0.01"
                      className="value-input"
                    />
                    <button
                      type="button"
                      onClick={() => removeCondition('price', index)}
                      className="remove-condition"
                    >
                      ×
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => addCondition('price')}
                  className="add-condition"
                >
                  + Add Price Condition
                </button>
              </div>
            )}
          </div>

          {/* Duration Conditions */}
          <div className="condition-category">
            <div className="condition-header">
              <label className="condition-checkbox">
                <input
                  type="checkbox"
                  checked={strategy.exclude_conditions.duration.enabled}
                  onChange={(e) => handleExcludeConditionChange('duration', 'enabled', e.target.checked)}
                />
                <h3>Duration Conditions</h3>
              </label>
            </div>
            
            {strategy.exclude_conditions.duration.enabled && (
              <div className="condition-inputs">
                {strategy.exclude_conditions.duration.conditions.map((condition, index) => (
                  <div key={index} className="condition-row">
                    <select
                      value={condition.comparator}
                      onChange={(e) => handleConditionChange('duration', index, 'comparator', e.target.value)}
                      className="comparator-select"
                    >
                      {COMPARATORS.map(comp => (
                        <option key={comp} value={comp}>{comp}</option>
                      ))}
                    </select>
                    <input
                      type="number"
                      value={condition.value}
                      onChange={(e) => handleConditionChange('duration', index, 'value', e.target.value)}
                      step="0.1"
                      className="value-input"
                    />
                    <button
                      type="button"
                      onClick={() => removeCondition('duration', index)}
                      className="remove-condition"
                    >
                      ×
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => addCondition('duration')}
                  className="add-condition"
                >
                  + Add Duration Condition
                </button>
              </div>
            )}
          </div>

          {/* Volume Conditions */}
          <div className="condition-category">
            <div className="condition-header">
              <label className="condition-checkbox">
                <input
                  type="checkbox"
                  checked={strategy.exclude_conditions.volume.enabled}
                  onChange={(e) => handleExcludeConditionChange('volume', 'enabled', e.target.checked)}
                />
                <h3>Trading Amount Conditions</h3>
              </label>
            </div>
            
            {strategy.exclude_conditions.volume.enabled && (
              <div className="condition-inputs">
                {strategy.exclude_conditions.volume.conditions.map((condition, index) => (
                  <div key={index} className="condition-row">
                    <select
                      value={condition.comparator}
                      onChange={(e) => handleConditionChange('volume', index, 'comparator', e.target.value)}
                      className="comparator-select"
                    >
                      {COMPARATORS.map(comp => (
                        <option key={comp} value={comp}>{comp}</option>
                      ))}
                    </select>
                    <input
                      type="number"
                      value={condition.value}
                      onChange={(e) => handleConditionChange('volume', index, 'value', e.target.value)}
                      step="100"
                      className="value-input"
                    />
                    <button
                      type="button"
                      onClick={() => removeCondition('volume', index)}
                      className="remove-condition"
                    >
                      ×
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => addCondition('volume')}
                  className="add-condition"
                >
                  + Add Volume Condition
                </button>
              </div>
            )}
          </div>
        </section>

        {/* Strategy Section */}
        <section className="config-section">
          <h2>Strategy Configuration</h2>
          
          <div className="section-content">
            <div className="input-group">
              <label>Hold Number:</label>
              <input
                type="number"
                value={strategy.hold_num}
                onChange={(e) => handleStrategyChange('hold_num', parseInt(e.target.value))}
              />
            </div>

            <div className="input-group">
              <label>Stop Profit (%):</label>
              <input
                type="number"
                step="0.01"
                value={strategy.stop_profit * 100}
                onChange={(e) => handleStrategyChange('stop_profit', parseFloat(e.target.value) / 100)}
              />
            </div>

            <div className="input-group">
              <label>Fee Rate (%):</label>
              <input
                type="number"
                step="0.001"
                value={strategy.fee_rate * 100}
                onChange={(e) => handleStrategyChange('fee_rate', parseFloat(e.target.value) / 100)}
              />
            </div>

            <div className="factors-section">
              <h3>Score Factors</h3>
              {strategy.score_factors.map((factor, index) => (
                <div key={factor} className="factor-group">
                  <label>{factor}:</label>
                  <input
                    type="number"
                    value={strategy.weights[index]}
                    onChange={(e) => {
                      const newWeights = [...strategy.weights];
                      newWeights[index] = Number(e.target.value);
                      setStrategy(prev => ({
                        ...prev,
                        weights: newWeights
                      }));
                    }}
                  />
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Buttons Section */}
        <div className="buttons-container">
          <button 
            className="generate-button"
            type="submit"
            onClick={handleGenerateConfig}
          >
            Generate Backtest
          </button>
          <button 
            className="reset-button"
            onClick={handleReset}
          >
            Reset
          </button>
        </div>
      </form>

      {/* JSON Output Section - will be removed when jsonOutput is null */}
      {jsonOutput && (
        <section className="json-output-section">
          <h2>Generated Configuration</h2>
          <div className="json-display">
            <pre>
              {JSON.stringify(jsonOutput, null, 4)
                .split('\n')
                //.map(line => line.trimLeft()) // Remove trailing whitespace
                .join('\n')}
            </pre>
            <button 
              className="copy-button"
              onClick={() => {
                navigator.clipboard.writeText(JSON.stringify(jsonOutput, null, 4));
                alert('Configuration copied to clipboard!');
              }}
            >
              Copy to Clipboard
            </button>
          </div>
        </section>
      )}
    </div>
  );
}
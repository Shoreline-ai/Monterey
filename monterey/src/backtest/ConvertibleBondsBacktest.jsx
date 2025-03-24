import { useState } from 'react';
import './ConvertibleBondsBacktest.css';

export default function ConvertibleBondsBacktest() {
  const COMPARATORS = ['<', '>', '==', '<=', '>='];

  // State for data section matching config.json
  const [data, setData] = useState({
    cb_data_path: '',
    index_data_path: '',
    start_date: '2022-08-01',
    end_date: '2025-12-31'
  });

  // State for strategy section matching config.json
  const [strategy, setStrategy] = useState({
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
  });

  // Add new state for JSON output
  const [jsonOutput, setJsonOutput] = useState(null);

  // Convert yyyy-MM-dd to yyyyMMdd for API/storage
  const getStorageFormat = (dateStr) => {
    return dateStr.replace(/-/g, '');
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

  // Modified submit handler
  const handleSubmit = (e) => {
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
  };

  return (
    <div className="backtest-container">
      <h1>Convertible Bond Backtesting</h1>
      
      <form onSubmit={handleSubmit}>
        {/* Data Section */}
        <section className="data-section">
          <h2>Data Configuration</h2>
          <div className="input-group">
            <label>Start Date:</label>
            <input
              type="date"
              value={data.start_date}
              onChange={handleDateChange('start_date')}
            />
            <span className="date-value">
              yyyyMMdd: {getDisplayFormat(data.start_date)}
            </span>
          </div>
          <div className="input-group">
            <label>End Date:</label>
            <input
              type="date"
              value={data.end_date}
              onChange={handleDateChange('end_date')}
            />
            <span className="date-value">
              yyyyMMdd: {getDisplayFormat(data.end_date)}
            </span>
          </div>
        </section>

        {/* Updated Exclude Conditions Section */}
        <section className="exclude-conditions-section">
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
        <section className="strategy-section">
          <h2>Strategy Configuration</h2>
          
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
                    newWeights[index] = parseInt(e.target.value);
                    handleStrategyChange('weights', newWeights);
                  }}
                />
              </div>
            ))}
          </div>
        </section>

        <button type="submit" className="submit-button">
          Generate Backtest
        </button>
      </form>

      {/* JSON Output Section */}
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
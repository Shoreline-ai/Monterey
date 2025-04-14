import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaRegCalendarAlt } from 'react-icons/fa';
import PageHeader from '../components/PageHeader.jsx';
import ConfigCard from '../components/ConfigCard.jsx';
import SectionHeader from '../components/SectionHeader.jsx';
import InputGroup from '../components/InputGroup.jsx';
import ConditionEditor from '../components/ConditionEditor.jsx';
import ScoreFactors from '../components/ScoreFactors.jsx';
import LoadingButton from '../components/LoadingButton.jsx';
import JsonDisplay from '../components/JsonDisplay.jsx';
import api from '../utils/axios';

export default function ConvertibleBondsBacktest() {
  const COMPARATORS = ['<', '>', '==', '<=', '>='];

  const initialState = {
    data: {
      start_date: '2022-08-01',
      end_date: '2025-12-31'
    },
    strategy: {
      exclude_conditions: {
        price: {
          enabled: true,
          conditions: [{ comparator: '<', value: 102 }, { comparator: '>', value: 155 }]
        },
        duration: {
          enabled: true,
          conditions: [{ comparator: '<', value: 0.7 }]
        },
        volume: {
          enabled: true,
          conditions: [{ comparator: '<', value: 1000 }]
        }
      },
      score_factors: ['bond_prem', 'ytm', 'turnover_5'],
      weights: [-10, 10, 5],
      hold_num: 5,
      stop_profit: 0.03,
      fee_rate: 0.002
    }
  };

  const [data, setData] = useState(initialState.data);
  const [strategy, setStrategy] = useState(initialState.strategy);
  const [jsonOutput, setJsonOutput] = useState(null);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) navigate('/login');
    setLoading(false);
  }, [navigate]);

  const handleGenerate = async () => {
    try {
      setIsGenerating(true);
      setError(null);

      const config = {
        data,
        strategies: [strategy],
        output_path: 'result/backtest_output.xlsx'
      };

      // should show the config in the json output
      setJsonOutput(config);

      const res = await api.post('/api/backtest', config);

      if (res.data.status === 'success') {
        setResults(res.data.performance);
      } else {
        throw new Error(res.data.message || 'Generation failed');
      }
    } catch (err) {
      console.error(err);
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      }
      setError(err.message || 'Generation error');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExcludeToggle = (category, enabled) => {
    setStrategy(prev => ({
      ...prev,
      exclude_conditions: {
        ...prev.exclude_conditions,
        [category]: {
          ...prev.exclude_conditions[category],
          enabled
        }
      }
    }));
  };

  const handleConditionChange = (category, index, field, value) => {
    setStrategy(prev => {
      const updated = { ...prev };
      updated.exclude_conditions[category].conditions[index][field] =
        field === 'value' ? Number(value) : value;
      return updated;
    });
  };

  const handleAddCondition = (category) => {
    setStrategy(prev => {
      const updated = { ...prev };
      updated.exclude_conditions[category].conditions.push({ comparator: '<', value: 0 });
      return updated;
    });
  };

  const handleRemoveCondition = (category, index) => {
    setStrategy(prev => {
      const updated = { ...prev };
      updated.exclude_conditions[category].conditions.splice(index, 1);
      return updated;
    });
  };

  const handleWeightChange = (index, value) => {
    setStrategy(prev => {
      const newWeights = [...prev.weights];
      newWeights[index] = value;
      return { ...prev, weights: newWeights };
    });
  };

  const handleStrategyValue = (key, value) => {
    setStrategy(prev => ({ ...prev, [key]: value }));
  };

  if (loading) return <div className="text-center mt-10 text-white">Loading...</div>;

  return (
    <div className="min-h-screen px-4 py-8 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      <div className="max-w-5xl mx-auto">
        <PageHeader />

        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-400 p-3 rounded text-sm mb-4">
            {error}
          </div>
        )}

        {/* Section: Dates */}
        <ConfigCard>
          <SectionHeader title="Data Configuration" />
          <InputGroup label="Start Date">
            <input
              type="date"
              value={data.start_date}
              onChange={(e) => setData({ ...data, start_date: e.target.value })}
              className="px-4 py-2 rounded-md bg-gray-800 border border-gray-600 text-white"
            />
          </InputGroup>
          <InputGroup label="End Date">
            <input
              type="date"
              value={data.end_date}
              onChange={(e) => setData({ ...data, end_date: e.target.value })}
              className="px-4 py-2 rounded-md bg-gray-800 border border-gray-600 text-white"
            />
          </InputGroup>
        </ConfigCard>

        {/* Section: Exclude Conditions */}
        <ConfigCard>
          <SectionHeader title="Exclude Conditions" />
          {['price', 'duration', 'volume'].map((key) => (
            <ConditionEditor
              key={key}
              title={key[0].toUpperCase() + key.slice(1) + ' Conditions'}
              enabled={strategy.exclude_conditions[key].enabled}
              onToggle={(e) => handleExcludeToggle(key, e.target.checked)}
              conditions={strategy.exclude_conditions[key].conditions}
              onChange={(index, field, value) => handleConditionChange(key, index, field, value)}
              onAdd={() => handleAddCondition(key)}
              onRemove={(index) => handleRemoveCondition(key, index)}
              COMPARATORS={COMPARATORS}
            />
          ))}
        </ConfigCard>

        {/* Section: Strategy */}
        <ConfigCard>
          <SectionHeader title="Strategy Configuration" />
          <InputGroup label="Hold Number">
            <input
              type="number"
              value={strategy.hold_num}
              onChange={(e) => handleStrategyValue('hold_num', Number(e.target.value))}
              className="px-4 py-2 rounded-md bg-gray-800 border border-gray-600 text-white"
            />
          </InputGroup>
          <InputGroup label="Stop Profit (%)">
            <input
              type="number"
              step="0.01"
              value={strategy.stop_profit * 100}
              onChange={(e) => handleStrategyValue('stop_profit', parseFloat(e.target.value) / 100)}
              className="px-4 py-2 rounded-md bg-gray-800 border border-gray-600 text-white"
            />
          </InputGroup>
          <InputGroup label="Fee Rate (%)">
            <input
              type="number"
              step="0.001"
              value={strategy.fee_rate * 100}
              onChange={(e) => handleStrategyValue('fee_rate', parseFloat(e.target.value) / 100)}
              className="px-4 py-2 rounded-md bg-gray-800 border border-gray-600 text-white"
            />
          </InputGroup>

          <div className="mt-6">
            <SectionHeader title="Score Factors" />
            <ScoreFactors
              scoreFactors={strategy.score_factors}
              weights={strategy.weights}
              onWeightChange={handleWeightChange}
            />
          </div>
        </ConfigCard>

        <div className="flex gap-4 mt-8">
          <div className="flex-1">
            <LoadingButton isLoading={isGenerating} onClick={handleGenerate}>
              Generate Backtest
            </LoadingButton>
          </div>
          <button
            onClick={() => {
              setStrategy(initialState.strategy);
              setData(initialState.data);
              setJsonOutput(initialState.strategy);
            }}
            className="flex-1 bg-red-600 hover:bg-red-500 transition py-3 rounded-md font-semibold shadow-md"
          >
            Reset
          </button>
        </div>

        {jsonOutput && <JsonDisplay json={jsonOutput} />}
      </div>
    </div>
  );
}

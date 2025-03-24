import { useState } from 'react';
import './Backtest.css';

// Add the 'export' keyword before the function declaration
export default function Backtest() {
  const commissionOptions = ['0', '0.1%', '0.2%', '0.3%', '0.4%', '0.5%'];
  const benchmarkOptions = ['转债等权', '中证1000', '国证2000', '沪深300'];
  const redemptionStatusOptions = [
    '已满足强赎条件',
    '公告实施强赎',
    '公告到期赎回',
    '已公告强赎',
    '强赎中'
  ];

  const marketOptions = [
    '沪市主板',
    '深市主板',
    '科创板',
    '北交所',
    '创业板'
  ];
  const industryOptions = [
    '金融行业',
    '科技行业',
    '医疗健康',
    '消费行业',
    '制造业',
    '能源行业',
    '房地产',
    '通信行业',
    '公用事业',
    '原材料'
  ];

  const companyTypeOptions = [
    '国有企业',
    '民营企业',
    '中外合资',
    '外商独资',
    '股份制企业',
    '上市公司',
    '集体企业'
  ];

  const regionOptions = [
    '华东',
    '华南',
    '华中',
    '华北',
    '西南',
    '西北',
    '东北'
  ];

  const externalRatingOptions = [
    'AAA',
    'AA+',
    'AA',
    'AA-',
    'A+',
    'A',
    'A-'
  ];

  const thirdPartyRatingOptions = [
    '优质',
    '良好',
    '一般',
    '较差',
    '风险'
  ];

  const specificBondOptions = [
    '转债A',
    '转债B',
    '转债C',
    // Add your specific bond options here
  ];

  const [holdingPeriod, setHoldingPeriod] = useState(10);
  const [holdingQuantity, setHoldingQuantity] = useState(10.00); // Add this line
  const [startDate, setStartDate] = useState('2024-03-07');
  const [endDate, setEndDate] = useState('2025-03-07');
  const [commission, setCommission] = useState(commissionOptions[0]); // Use first option as default
  const [excludeValue, setExcludeValue] = useState(3);
  const [tradingTime, setTradingTime] = useState('same-day'); // Add new state for trading time
  const [useProfitForNew, setUseProfitForNew] = useState(true);
  const [benchmark, setBenchmark] = useState(benchmarkOptions[0]); // Add new state

  const [redemptionStatus, setRedemptionStatus] = useState([]); // Using array for multiple selection
  const [excludeMarket, setExcludeMarket] = useState('');
  const [excludeIndustry, setExcludeIndustry] = useState('');
  const [excludeCompanyType, setExcludeCompanyType] = useState('');

  const [excludeRegion, setExcludeRegion] = useState('');
  const [excludeExternalRating, setExcludeExternalRating] = useState('');
  const [excludeThirdPartyRating, setExcludeThirdPartyRating] = useState('');
  const [excludeSpecificBond, setExcludeSpecificBond] = useState('');


  const handleRedemptionChange = (e) => {
    const value = Array.from(e.target.selectedOptions, option => option.value);
    setRedemptionStatus(value);
  };
  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);

    const payload = {
      basicSettings: {
        holdingPeriod,
        holdingQuantity,
        dateRange: {
          startDate,
          endDate
        },
        commission,
        tradingTime, // Add trading time to payload
        benchmark, // Add benchmark to payload
        useProfitForNew
      },
      factorSettings: {
        redemptionStatus,
        excludeValue,
        excludeMarket,
        excludeIndustry
      }
    };

    // ... rest of submit function
  };

  return (
    <div className="backtest-container">
      {/* 基础设置 */}
      <div className="basic-settings">
        <div className="setting-group">
          <label>持有周期</label>
          <input 
            type="number" 
            value={holdingPeriod} 
            onChange={(e) => setHoldingPeriod(e.target.value)}
          />
        </div>

        {/* Add new input box */}
        <div className="setting-group">
          <label>持有数量</label>
          <input 
            type="number"
            step="0.01"
            value={holdingQuantity}
            onChange={(e) => setHoldingQuantity(parseFloat(e.target.value))}
          />
        </div>
        
        <div className="setting-group">
          <label>回测时间</label>
          <div className="date-range">
            <input 
              type="date" 
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
            <span>至</span>
            <input 
              type="date" 
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
        </div>

        {/* Add new dropdown for commission */}
        <div className="setting-group">
          <label>佣金和滑点</label>
          <select 
            value={commission}
            onChange={(e) => setCommission(e.target.value)}
            className="commission-select"
          >
            {commissionOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        <div className="setting-group trading-time">
          <label>换仓时间</label>
          <div className="radio-options">
            <div className="radio-option">
              <input
                type="radio"
                id="same-day"
                name="trading-time"
                value="same-day"
                checked={tradingTime === 'same-day'}
                onChange={(e) => setTradingTime(e.target.value)}
              />
              <label htmlFor="same-day">
                收盘时以收盘价卖出更换的旧标的，同时以收盘价买入新标的
              </label>
            </div>
            <div className="radio-option">
              <input
                type="radio"
                id="next-day"
                name="trading-time"
                value="next-day"
                checked={tradingTime === 'next-day'}
                onChange={(e) => setTradingTime(e.target.value)}
              />
              <label htmlFor="next-day">
                收盘时以收盘价卖出所有的旧标的，下个交易日开盘时以开盘价买入新标的
              </label>
            </div>
          </div>
        </div>
        
        <div className="setting-group">
          <label>基准指标</label>
          <select 
            value={benchmark}
            onChange={(e) => setBenchmark(e.target.value)}
            className="benchmark-select"
          >
            {benchmarkOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 因子设置 */}
      <div className="factor-settings">
        <h3>因子设置</h3>
        <div className="exclude-settings">
          <div className="setting-group">
            <label>排除新值</label>
            <input 
              type="number" 
              value={excludeValue}
              onChange={(e) => setExcludeValue(e.target.value)}
            />
          </div>

          {/* Add new dropdown for redemption status */}
          <div className="setting-group">
            <label>排除赎回状态</label>
            <select 
                multiple
                value={redemptionStatus}
                onChange={handleRedemptionChange}
                className="select-input"
                >
              <option value="">请选择要排除的状态</option>
              {redemptionStatusOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div className="setting-group">
            <label>排除市场</label>
            <select 
              value={excludeMarket || ''}
              onChange={(e) => setExcludeMarket(e.target.value)}
              className="select-input"
            >
              <option value="">请选择要排除的市场</option>
              {marketOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div className="setting-group">
            <label>排除行业</label>
            <select 
              value={excludeIndustry || ''}
              onChange={(e) => setExcludeIndustry(e.target.value)}
              className="select-input"
            >
              <option value="">请选择要排除的行业</option>
              {industryOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div className="setting-group">
            <label>排除企业类型</label>
            <select 
              value={excludeCompanyType || ''}
              onChange={(e) => setExcludeCompanyType(e.target.value)}
              className="select-input"
            >
              <option value="">请选择要排除的企业类型</option>
              {companyTypeOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
          
          <div className="setting-group">
            <label>排除地域</label>
            <select 
              value={excludeRegion || ''}
              onChange={(e) => setExcludeRegion(e.target.value)}
              className="select-input"
            >
              <option value="">请选择要排除的地域</option>
              {regionOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          {/* Add new dropdown for external rating */}
          <div className="setting-group">
            <label>排除外部评级</label>
            <select 
              value={excludeExternalRating || ''}
              onChange={(e) => setExcludeExternalRating(e.target.value)}
              className="select-input"
            >
              <option value="">请选择要排除的外部评级</option>
              {externalRatingOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div className="setting-group">
            <label>排除三方评级</label>
            <select 
              value={excludeThirdPartyRating || ''}
              onChange={(e) => setExcludeThirdPartyRating(e.target.value)}
              className="select-input"
            >
              <option value="">请选择要排除的三方评级</option>
              {thirdPartyRatingOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          {/* Add new dropdown for specific bonds */}
          <div className="setting-group">
            <label>排除指定转债</label>
            <select 
              value={excludeSpecificBond || ''}
              onChange={(e) => setExcludeSpecificBond(e.target.value)}
              className="select-input"
            >
              <option value="">请选择要排除的转债</option>
              {specificBondOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          {/* 其他排除选项 */}
          <div className="setting-group">
            <label>排除ST</label>
            <input type="checkbox" />
          </div>
        </div>
      </div>

      {/* 选择因子区域 */}
      <div className="factor-selection">
        <div className="tabs">
          <button className="tab active">基础因子</button>
          <button className="tab">历史类因子</button>
          <button className="tab">正股相关因子</button>
          <button className="tab">自定义因子</button>
        </div>
      </div>
    </div>
  );
}
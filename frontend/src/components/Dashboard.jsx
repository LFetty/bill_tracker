import { useState, useEffect } from 'react';
import { getSpendingSummary, getBills, getStoreSummary, getStoreItemComparison } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

const COLORS = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22'];

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [storeSummary, setStoreSummary] = useState(null);
  const [recentBills, setRecentBills] = useState([]);
  const [storeComparison, setStoreComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    fetchData();
  }, [currentDate]);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Get first and last day of selected month
      const startDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      const endDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0, 23, 59, 59);

      const params = {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString()
      };

      const [summaryRes, billsRes, storeRes, comparisonRes] = await Promise.all([
        getSpendingSummary(params),
        getBills({ ...params, limit: 5 }),
        getStoreSummary(params),
        getStoreItemComparison(params)
      ]);

      setSummary(summaryRes.data);
      setRecentBills(billsRes.data);
      setStoreSummary(storeRes.data);
      setStoreComparison(comparisonRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const formatMonthYear = (date) => {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  // Prepare data for charts
  const categoryData = summary ? Object.entries(summary.categories).map(([name, data]) => ({
    name,
    value: parseFloat(data.total.toFixed(2))
  })) : [];

  if (summary && summary.uncategorized > 0) {
    categoryData.push({
      name: 'Uncategorized',
      value: parseFloat(summary.uncategorized.toFixed(2))
    });
  }

  // Prepare subcategory data for bar chart
  const subcategoryData = [];
  if (summary) {
    Object.entries(summary.categories).forEach(([categoryName, categoryData]) => {
      Object.entries(categoryData.subcategories).forEach(([subName, amount]) => {
        subcategoryData.push({
          name: `${categoryName} - ${subName}`,
          amount: parseFloat(amount.toFixed(2))
        });
      });
    });
  }
  subcategoryData.sort((a, b) => b.amount - a.amount);
  const topSubcategories = subcategoryData.slice(0, 8);

  return (
    <div className="container">
      <h1 style={{ marginBottom: '1rem', color: '#2c3e50' }}>Dashboard</h1>

      {/* Month Navigation */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '2rem',
        marginBottom: '2rem',
        padding: '1rem',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px'
      }}>
        <button
          onClick={goToPreviousMonth}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '1.5rem',
            backgroundColor: '#3498db',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          ←
        </button>
        <h2 style={{ margin: 0, color: '#2c3e50', minWidth: '200px', textAlign: 'center' }}>
          {formatMonthYear(currentDate)}
        </h2>
        <button
          onClick={goToNextMonth}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '1.5rem',
            backgroundColor: '#3498db',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          →
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3 style={{ color: '#7f8c8d', marginBottom: '0.5rem' }}>Total Spending</h3>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2c3e50' }}>
            ${summary?.total?.toFixed(2) || '0.00'}
          </div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3 style={{ color: '#7f8c8d', marginBottom: '0.5rem' }}>Categories</h3>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#3498db' }}>
            {Object.keys(summary?.categories || {}).length}
          </div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3 style={{ color: '#7f8c8d', marginBottom: '0.5rem' }}>Recent Bills</h3>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2ecc71' }}>
            {recentBills.length}
          </div>
        </div>
      </div>

      {categoryData.length > 0 && (
        <div className="card">
          <h2>Spending by Category</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, value }) => `${name}: $${value}`}
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `$${value}`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {topSubcategories.length > 0 && (
        <div className="card">
          <h2>Top Subcategories</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topSubcategories}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip formatter={(value) => `$${value}`} />
              <Bar dataKey="amount" fill="#3498db" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {storeSummary && Object.keys(storeSummary.stores || {}).length > 0 && (
        <div className="card">
          <h2>Spending by Store</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={Object.entries(storeSummary.stores).map(([name, data]) => ({
              name,
              total: parseFloat(data.total.toFixed(2)),
              bills: data.bill_count
            })).sort((a, b) => b.total - a.total).slice(0, 10)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip formatter={(value) => `$${value}`} />
              <Bar dataKey="total" fill="#2ecc71" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="card">
        <h2>Recent Bills</h2>
        {recentBills.length === 0 ? (
          <p>No bills yet. Upload your first bill to get started!</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Store</th>
                <th>Items</th>
                <th>Total</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {recentBills.map((bill) => (
                <tr key={bill.id}>
                  <td>{new Date(bill.date).toLocaleDateString()}</td>
                  <td>{bill.store_name || '-'}</td>
                  <td>{bill.items.length} items</td>
                  <td>${bill.total.toFixed(2)}</td>
                  <td>{bill.notes || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Store Item Comparison */}
      {storeComparison && storeComparison.items && storeComparison.items.length > 0 && (
        <div className="card">
          <h2>Store Item Comparison</h2>
          <p style={{ color: '#7f8c8d', marginBottom: '1rem' }}>
            Compare prices of the same items across different stores
          </p>
          <table className="table">
            <thead>
              <tr>
                <th>Product Name</th>
                <th>Stores</th>
                <th>Price Range</th>
                <th>Average Price</th>
              </tr>
            </thead>
            <tbody>
              {storeComparison.items.map((item, index) => (
                <tr key={index}>
                  <td style={{ fontWeight: 'bold' }}>{item.product_name}</td>
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      {item.stores.map((store, idx) => (
                        <div key={idx} style={{ fontSize: '0.9rem' }}>
                          <strong>{store.store_name || 'Unknown Store'}:</strong> ${store.amount.toFixed(2)}
                        </div>
                      ))}
                    </div>
                  </td>
                  <td>
                    ${Math.min(...item.stores.map(s => s.amount)).toFixed(2)} -
                    ${Math.max(...item.stores.map(s => s.amount)).toFixed(2)}
                  </td>
                  <td>
                    ${(item.stores.reduce((sum, s) => sum + s.amount, 0) / item.stores.length).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Dashboard;

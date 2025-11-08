import { useState, useEffect } from 'react';
import { getBills, deleteBill, scanBill, createBill, getCategories } from '../services/api';

function Bills() {
  const [bills, setBills] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showManualModal, setShowManualModal] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [ocrResult, setOcrResult] = useState(null);
  const [editableItems, setEditableItems] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [billsRes, categoriesRes] = await Promise.all([
        getBills(),
        getCategories()
      ]);
      setBills(billsRes.data);
      setCategories(categoriesRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to load bills');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleScanBill = async () => {
    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      const response = await scanBill(selectedFile);
      setOcrResult(response.data);
      setEditableItems(response.data.items.map(item => ({
        product_name: item.product_name,
        amount: item.amount,
        subcategory_id: item.suggested_subcategory_id || null,
        category_id: item.suggested_subcategory_id ? getCategoryForSubcategory(item.suggested_subcategory_id) : null
      })));
      setShowManualModal(true);
      setShowUploadModal(false);
    } catch (err) {
      setError('Failed to scan bill. Make sure Tesseract OCR is installed on the server.');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleSaveBill = async () => {
    try {
      const total = editableItems.reduce((sum, item) => sum + parseFloat(item.amount || 0), 0);
      await createBill({
        items: editableItems.map(item => ({
          product_name: item.product_name,
          amount: item.amount,
          subcategory_id: item.subcategory_id
        })),
        total,
        notes: ocrResult ? 'Imported via OCR' : 'Manually entered'
      });
      setSuccess('Bill saved successfully!');
      setShowManualModal(false);
      setOcrResult(null);
      setEditableItems([]);
      setSelectedFile(null);
      fetchData();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to save bill');
      console.error(err);
    }
  };

  const handleDeleteBill = async (id) => {
    if (!confirm('Are you sure you want to delete this bill?')) {
      return;
    }
    try {
      await deleteBill(id);
      setSuccess('Bill deleted successfully!');
      fetchData();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to delete bill');
      console.error(err);
    }
  };

  const openManualBillModal = () => {
    setOcrResult(null);
    setEditableItems([{ product_name: '', amount: 0, subcategory_id: null, category_id: null }]);
    setShowManualModal(true);
  };

  const updateItem = (index, field, value) => {
    const updated = [...editableItems];
    updated[index][field] = value;

    // If category changes, reset subcategory
    if (field === 'category_id') {
      updated[index].subcategory_id = null;
    }

    setEditableItems(updated);
  };

  const removeItem = (index) => {
    setEditableItems(editableItems.filter((_, i) => i !== index));
  };

  const addItem = () => {
    setEditableItems([...editableItems, { product_name: '', amount: 0, subcategory_id: null, category_id: null }]);
  };

  // Get subcategories for a specific category
  const getSubcategoriesForCategory = (categoryId) => {
    if (!categoryId) return [];
    const category = categories.find(cat => cat.id === parseInt(categoryId));
    return category ? category.subcategories : [];
  };

  // Get category ID for a subcategory
  const getCategoryForSubcategory = (subcategoryId) => {
    if (!subcategoryId) return null;
    for (const category of categories) {
      const hasSubcat = category.subcategories.some(sub => sub.id === subcategoryId);
      if (hasSubcat) return category.id;
    }
    return null;
  };

  if (loading) {
    return <div className="loading">Loading bills...</div>;
  }

  return (
    <div className="container">
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <h1 style={{ color: '#2c3e50' }}>Bills</h1>
        <div className="flex" style={{ gap: '0.5rem' }}>
          <button className="btn btn-success" onClick={openManualBillModal}>
            Add Manual Bill
          </button>
          <button className="btn btn-primary" onClick={() => setShowUploadModal(true)}>
            Upload Bill (OCR)
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {bills.length === 0 ? (
        <div className="card">
          <p>No bills yet. Upload your first bill to get started!</p>
        </div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Items</th>
                <th>Total</th>
                <th>Notes</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {bills.map((bill) => (
                <tr key={bill.id}>
                  <td>{new Date(bill.date).toLocaleDateString()}</td>
                  <td>
                    {bill.items.length} items
                    <details style={{ marginTop: '0.5rem' }}>
                      <summary style={{ cursor: 'pointer', color: '#3498db' }}>View items</summary>
                      <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                        {bill.items.map((item, idx) => (
                          <li key={idx} style={{ marginBottom: '0.25rem' }}>
                            {item.product_name} - ${item.amount.toFixed(2)}
                            {item.subcategory && (
                              <span style={{ color: '#7f8c8d', fontSize: '0.85rem' }}>
                                {' '}({item.subcategory.name})
                              </span>
                            )}
                          </li>
                        ))}
                      </ul>
                    </details>
                  </td>
                  <td>${bill.total.toFixed(2)}</td>
                  <td>{bill.notes || '-'}</td>
                  <td>
                    <button
                      className="btn btn-danger"
                      onClick={() => handleDeleteBill(bill.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="modal-overlay" onClick={() => !uploading && setShowUploadModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Upload Bill</h2>
              <button className="close-btn" onClick={() => !uploading && setShowUploadModal(false)}>
                &times;
              </button>
            </div>
            <div className="form-group">
              <label>Select Bill Image</label>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                disabled={uploading}
              />
            </div>
            {selectedFile && (
              <p style={{ color: '#2ecc71', marginBottom: '1rem' }}>
                Selected: {selectedFile.name}
              </p>
            )}
            <div className="flex" style={{ justifyContent: 'flex-end' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowUploadModal(false)}
                disabled={uploading}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleScanBill}
                disabled={!selectedFile || uploading}
              >
                {uploading ? 'Scanning...' : 'Scan Bill'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Manual Edit Modal */}
      {showManualModal && (
        <div className="modal-overlay">
          <div className="modal" style={{ maxWidth: '800px' }}>
            <div className="modal-header">
              <h2>Review & Edit Bill Items</h2>
              <button className="close-btn" onClick={() => setShowManualModal(false)}>
                &times;
              </button>
            </div>

            {ocrResult && (
              <div style={{ marginBottom: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                <strong>Raw OCR Text:</strong>
                <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                  {ocrResult.raw_text}
                </pre>
              </div>
            )}

            <div style={{ marginBottom: '1rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Items</h3>
              {editableItems.map((item, index) => {
                const availableSubcategories = getSubcategoriesForCategory(item.category_id);
                return (
                  <div key={index} className="bill-item">
                    <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '2fr 1fr 1.5fr 1.5fr auto', gap: '0.5rem', alignItems: 'center' }}>
                      <input
                        type="text"
                        value={item.product_name}
                        onChange={(e) => updateItem(index, 'product_name', e.target.value)}
                        placeholder="Product name"
                      />
                      <input
                        type="number"
                        step="0.01"
                        value={item.amount}
                        onChange={(e) => updateItem(index, 'amount', e.target.value)}
                        placeholder="Amount"
                      />
                      <select
                        value={item.category_id || ''}
                        onChange={(e) => updateItem(index, 'category_id', e.target.value ? parseInt(e.target.value) : null)}
                      >
                        <option value="">Select Category</option>
                        {categories.map(cat => (
                          <option key={cat.id} value={cat.id}>
                            {cat.name}
                          </option>
                        ))}
                      </select>
                      <select
                        value={item.subcategory_id || ''}
                        onChange={(e) => updateItem(index, 'subcategory_id', e.target.value ? parseInt(e.target.value) : null)}
                        disabled={!item.category_id}
                      >
                        <option value="">Select Subcategory</option>
                        {availableSubcategories.map(sub => (
                          <option key={sub.id} value={sub.id}>
                            {sub.name}
                          </option>
                        ))}
                      </select>
                      <button
                        className="btn btn-danger"
                        onClick={() => removeItem(index)}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                );
              })}
              <button className="btn btn-secondary" onClick={addItem} style={{ marginTop: '0.5rem' }}>
                Add Item
              </button>
            </div>

            <div style={{ marginBottom: '1rem', padding: '1rem', backgroundColor: '#e8f4f8', borderRadius: '4px' }}>
              <strong>Total: ${editableItems.reduce((sum, item) => sum + parseFloat(item.amount || 0), 0).toFixed(2)}</strong>
            </div>

            <div className="flex" style={{ justifyContent: 'flex-end' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowManualModal(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-success"
                onClick={handleSaveBill}
              >
                Save Bill
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Bills;

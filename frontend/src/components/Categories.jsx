import { useState, useEffect } from 'react';
import { getCategories, createCategory, createSubcategory, updateSubcategory, deleteCategory, deleteSubcategory } from '../services/api';

function Categories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [showSubcategoryModal, setShowSubcategoryModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedSubcategory, setSelectedSubcategory] = useState(null);

  const [categoryForm, setCategoryForm] = useState({ name: '', description: '' });
  const [subcategoryForm, setSubcategoryForm] = useState({
    name: '',
    description: '',
    category_id: null,
    keywords: ''
  });

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await getCategories();
      setCategories(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load categories');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCategory = async (e) => {
    e.preventDefault();
    try {
      await createCategory(categoryForm);
      setCategoryForm({ name: '', description: '' });
      setShowCategoryModal(false);
      fetchCategories();
    } catch (err) {
      setError('Failed to create category');
      console.error(err);
    }
  };

  const handleCreateSubcategory = async (e) => {
    e.preventDefault();
    try {
      const keywords = subcategoryForm.keywords
        .split(',')
        .map(k => k.trim())
        .filter(k => k.length > 0);

      await createSubcategory({
        name: subcategoryForm.name,
        description: subcategoryForm.description,
        category_id: subcategoryForm.category_id,
        keywords
      });

      setSubcategoryForm({ name: '', description: '', category_id: null, keywords: '' });
      setShowSubcategoryModal(false);
      fetchCategories();
    } catch (err) {
      setError('Failed to create subcategory');
      console.error(err);
    }
  };

  const handleDeleteCategory = async (id) => {
    if (!confirm('Are you sure? This will delete all subcategories and unlink bill items.')) {
      return;
    }
    try {
      await deleteCategory(id);
      fetchCategories();
    } catch (err) {
      setError('Failed to delete category');
      console.error(err);
    }
  };

  const handleDeleteSubcategory = async (id) => {
    if (!confirm('Are you sure? This will unlink bill items from this subcategory.')) {
      return;
    }
    try {
      await deleteSubcategory(id);
      fetchCategories();
    } catch (err) {
      setError('Failed to delete subcategory');
      console.error(err);
    }
  };

  const openSubcategoryModal = (categoryId) => {
    setSubcategoryForm({ ...subcategoryForm, category_id: categoryId });
    setShowSubcategoryModal(true);
  };

  if (loading) {
    return <div className="loading">Loading categories...</div>;
  }

  return (
    <div className="container">
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <h1 style={{ color: '#2c3e50' }}>Categories & Subcategories</h1>
        <button className="btn btn-primary" onClick={() => setShowCategoryModal(true)}>
          Add Category
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {categories.length === 0 ? (
        <div className="card">
          <p>No categories yet. Create your first category to get started!</p>
        </div>
      ) : (
        <ul className="category-tree">
          {categories.map((category) => (
            <li key={category.id} className="category-item">
              <div className="flex-between">
                <div>
                  <h3 style={{ marginBottom: '0.5rem' }}>{category.name}</h3>
                  {category.description && (
                    <p style={{ color: '#7f8c8d', fontSize: '0.9rem' }}>{category.description}</p>
                  )}
                </div>
                <div className="flex" style={{ gap: '0.5rem' }}>
                  <button
                    className="btn btn-success"
                    onClick={() => openSubcategoryModal(category.id)}
                  >
                    Add Subcategory
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleDeleteCategory(category.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>

              {category.subcategories && category.subcategories.length > 0 && (
                <ul className="subcategory-list">
                  {category.subcategories.map((subcat) => (
                    <li key={subcat.id} className="subcategory-item">
                      <div className="flex-between">
                        <div style={{ flex: 1 }}>
                          <strong>{subcat.name}</strong>
                          {subcat.description && (
                            <p style={{ color: '#7f8c8d', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                              {subcat.description}
                            </p>
                          )}
                          {subcat.keywords && subcat.keywords.length > 0 && (
                            <div className="keyword-tags">
                              {subcat.keywords.map((kw, idx) => (
                                <span key={idx} className="keyword-tag">
                                  {kw.keyword}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        <button
                          className="btn btn-danger"
                          style={{ marginLeft: '1rem' }}
                          onClick={() => handleDeleteSubcategory(subcat.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      )}

      {/* Category Modal */}
      {showCategoryModal && (
        <div className="modal-overlay" onClick={() => setShowCategoryModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add Category</h2>
              <button className="close-btn" onClick={() => setShowCategoryModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleCreateCategory}>
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={categoryForm.name}
                  onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={categoryForm.description}
                  onChange={(e) => setCategoryForm({ ...categoryForm, description: e.target.value })}
                  rows="3"
                />
              </div>
              <div className="flex" style={{ justifyContent: 'flex-end' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowCategoryModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Subcategory Modal */}
      {showSubcategoryModal && (
        <div className="modal-overlay" onClick={() => setShowSubcategoryModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add Subcategory</h2>
              <button className="close-btn" onClick={() => setShowSubcategoryModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleCreateSubcategory}>
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={subcategoryForm.name}
                  onChange={(e) => setSubcategoryForm({ ...subcategoryForm, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={subcategoryForm.description}
                  onChange={(e) => setSubcategoryForm({ ...subcategoryForm, description: e.target.value })}
                  rows="2"
                />
              </div>
              <div className="form-group">
                <label>Keywords (comma-separated)</label>
                <input
                  type="text"
                  value={subcategoryForm.keywords}
                  onChange={(e) => setSubcategoryForm({ ...subcategoryForm, keywords: e.target.value })}
                  placeholder="e.g., gas, fuel, petrol"
                />
                <small style={{ color: '#7f8c8d', display: 'block', marginTop: '0.25rem' }}>
                  Keywords are used for automatic categorization of products
                </small>
              </div>
              <div className="flex" style={{ justifyContent: 'flex-end' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowSubcategoryModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Categories;

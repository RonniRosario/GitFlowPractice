/**
 * StockFlow - Product Management System CRUD
 * Standard Vanilla JS code for Git Flow practice base.
 */

// Application State
let products = [];
const STORAGE_KEY = 'stockflow_products';

// DOM Elements
let productModal;
const alertContainer = document.getElementById('alert-container');
const productTableBody = document.getElementById('product-table-body');
const emptyState = document.getElementById('empty-state');
const productForm = document.getElementById('productForm');
const productIdInput = document.getElementById('productId');
const productNameInput = document.getElementById('productName');
const productCategoryInput = document.getElementById('productCategory');
const productPriceInput = document.getElementById('productPrice');
const productModalLabel = document.getElementById('productModalLabel');
const btnAddProduct = document.getElementById('btn-add-product');
const searchInput = document.getElementById('search-input');
const categoryFilter = document.getElementById('category-filter');
const productCounter = document.getElementById('product-counter');
const productSort = document.getElementById('product-sort');

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Bootstrap Modal instance
  productModal = new bootstrap.Modal(document.getElementById('productModal'));
  
  // Load initial data and render
  loadProducts();
  
  // Event Listeners
  setupEventListeners();
});

/**
 * Attaches event handlers to various DOM elements.
 */
function setupEventListeners() {
  // Form submission handling
  productForm.addEventListener('submit', handleFormSubmit);
  
  // Reset form styling when modal is closed
  document.getElementById('productModal').addEventListener('hidden.bs.modal', resetForm);
  
  // Configure action on clicking the header "Add Product" button
  btnAddProduct.addEventListener('click', () => {
    productModalLabel.textContent = 'Add Product';
    productIdInput.value = '';
  });

  // Filter products as the user types
  if (searchInput) {
    searchInput.addEventListener('input', renderProducts);
  }

  // Filter products as the user changes category
  if (categoryFilter) {
    categoryFilter.addEventListener('change', renderProducts);
  }

  // Sort products as the user changes sorting option
  if (productSort) {
    productSort.addEventListener('change', renderProducts);
  }
}

/**
 * Loads products list from LocalStorage.
 */
function loadProducts() {
  const storedData = localStorage.getItem(STORAGE_KEY);
  if (storedData) {
    try {
      products = JSON.parse(storedData);
    } catch (e) {
      showAlert('Error loading stored products. Starting fresh.', 'danger');
      products = [];
    }
  } else {
    products = [];
  }
  renderProducts();
}

/**
 * Saves products list to LocalStorage.
 */
function saveProducts() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(products));
}

/**
 * Renders products list into the table.
 * Displays empty state illustration if list is empty.
 */
function renderProducts() {
  productTableBody.innerHTML = '';
  
  if (products.length === 0) {
    if (searchInput) searchInput.value = '';
    if (categoryFilter) categoryFilter.value = '';
    if (productSort) productSort.value = 'default';
    updateProductCounter(0);
    emptyState.querySelector('h5').textContent = 'No products found';
    emptyState.querySelector('p').textContent = 'Get started by creating your first product using the "Add Product" button above.';
    emptyState.classList.remove('d-none');
    return;
  }
  
  const searchTerm = searchInput ? searchInput.value.trim().toLowerCase() : '';
  const selectedCategory = categoryFilter ? categoryFilter.value : '';
  
  let filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm);
    const matchesCategory = selectedCategory === '' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const sortVal = productSort ? productSort.value : 'default';
  if (sortVal !== 'default') {
    filteredProducts.sort((a, b) => {
      if (sortVal === 'name-asc') {
        return a.name.localeCompare(b.name);
      } else if (sortVal === 'name-desc') {
        return b.name.localeCompare(a.name);
      } else if (sortVal === 'price-asc') {
        return a.price - b.price;
      } else if (sortVal === 'price-desc') {
        return b.price - a.price;
      }
      return 0;
    });
  }
  
  if (filteredProducts.length === 0) {
    updateProductCounter(0);
    emptyState.querySelector('h5').textContent = 'No matching products found';
    emptyState.querySelector('p').textContent = 'Try adjusting your search or category filter.';
    emptyState.classList.remove('d-none');
    return;
  }
  
  updateProductCounter(filteredProducts.length);
  emptyState.classList.add('d-none');
  
  filteredProducts.forEach(product => {
    const row = document.createElement('tr');
    
    // Formatting price as USD currency
    const formattedPrice = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(product.price);
    
    row.innerHTML = `
      <td>
        <span class="fw-semibold text-dark">${escapeHtml(product.name)}</span>
      </td>
      <td>
        <span class="badge bg-light text-secondary border px-2 py-1.5">${escapeHtml(product.category)}</span>
      </td>
      <td class="font-monospace">${formattedPrice}</td>
      <td class="text-end">
        <div class="btn-group" role="group">
          <button class="btn btn-outline-secondary btn-action me-1 btn-edit" data-id="${product.id}" title="Edit Product">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-outline-danger btn-action btn-delete" data-id="${product.id}" title="Delete Product">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </td>
    `;
    
    // Add event handlers directly to buttons in the row
    row.querySelector('.btn-edit').addEventListener('click', () => openEditModal(product.id));
    row.querySelector('.btn-delete').addEventListener('click', () => handleDelete(product.id));
    
    productTableBody.appendChild(row);
  });
}

/**
 * Populates form fields and triggers the edit modal.
 * @param {string} id - Product ID
 */
function openEditModal(id) {
  const product = products.find(p => p.id === id);
  if (!product) {
    showAlert('Requested product could not be found.', 'danger');
    return;
  }
  
  // Populate form values
  productIdInput.value = product.id;
  productNameInput.value = product.name;
  productCategoryInput.value = product.category;
  productPriceInput.value = product.price;
  
  // Modify Modal Label
  productModalLabel.textContent = 'Edit Product';
  
  // Show Modal
  productModal.show();
}

/**
 * Handles Form submissions for both Create and Update operations.
 */
function handleFormSubmit(event) {
  event.preventDefault();
  
  const id = productIdInput.value;
  const name = productNameInput.value.trim();
  const category = productCategoryInput.value;
  const price = parseFloat(productPriceInput.value);

  // Check for duplicate product name (case-insensitive)
  const isDuplicate = products.some(p => p.id !== id && p.name.trim().toLowerCase() === name.toLowerCase());

  if (isDuplicate) {
    productNameInput.setCustomValidity("A product with this name already exists.");
    const feedback = productNameInput.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
      feedback.textContent = "A product with this name already exists.";
    }
  } else {
    productNameInput.setCustomValidity("");
    const feedback = productNameInput.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
      feedback.textContent = "Please enter a valid product name.";
    }
  }
  
  // Custom Bootstrap Form Validation visual states
  if (!productForm.checkValidity()) {
    event.stopPropagation();
    productForm.classList.add('was-validated');
    return;
  }
  
  if (id) {
    // Edit flow
    const index = products.findIndex(p => p.id === id);
    if (index !== -1) {
      products[index] = { id, name, category, price };
      saveProducts();
      renderProducts();
      showAlert('Product updated successfully.', 'success');
    } else {
      showAlert('Failed to update product.', 'danger');
    }
  } else {
    // Create flow
    const newProduct = {
      id: Date.now().toString(),
      name,
      category,
      price
    };
    products.push(newProduct);
    saveProducts();
    renderProducts();
    showAlert('Product added successfully.', 'success');
  }
  
  productModal.hide();
}

/**
 * Deletes a product from the list and storage.
 * @param {string} id - Product ID
 */
function handleDelete(id) {
  const index = products.findIndex(p => p.id === id);
  if (index === -1) {
    showAlert('Unable to delete. Product not found.', 'danger');
    return;
  }
  
  // Remove element and update storage/UI
  products.splice(index, 1);
  saveProducts();
  renderProducts();
  showAlert('Product deleted successfully.', 'success');
}

/**
 * Resets form validations and fields when closing or opening.
 */
function resetForm() {
  productForm.reset();
  productForm.classList.remove('was-validated');
  productIdInput.value = '';
  productNameInput.setCustomValidity('');
  const feedback = productNameInput.nextElementSibling;
  if (feedback && feedback.classList.contains('invalid-feedback')) {
    feedback.textContent = "Please enter a valid product name.";
  }
}

/**
 * Displays a simple success/error notification alert.
 * Automatically fades and removes itself after 3 seconds.
 * @param {string} message - Text notification message
 * @param {string} type - Bootstrap context type (success, danger, warning)
 */
function showAlert(message, type = 'success') {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.role = 'alert';
  
  // Set appropriate icons
  let icon = 'bi-check-circle-fill';
  if (type === 'danger') icon = 'bi-exclamation-triangle-fill';
  if (type === 'warning') icon = 'bi-exclamation-circle-fill';
  
  alertDiv.innerHTML = `
    <i class="bi ${icon} fs-5"></i>
    <div>${message}</div>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  alertContainer.appendChild(alertDiv);
  
  // Automatic dismissal
  setTimeout(() => {
    // Check if element is still in the document
    if (alertDiv.parentNode) {
      // Use Bootstrap alert close trigger to fade out correctly
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alertDiv);
      bsAlert.close();
    }
  }, 3000);
}

/**
 * Escapes HTML string to prevent XSS.
 * @param {string} str - Raw string
 * @returns {string} Safe escaped string
 */
function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Updates the product counter display with the given count.
 * @param {number} count - Number of visible products
 */
function updateProductCounter(count) {
  if (!productCounter) return;
  if (count === 1) {
    productCounter.textContent = '1 product';
  } else {
    productCounter.textContent = `${count} products`;
  }
}


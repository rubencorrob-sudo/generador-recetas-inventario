const state = {
  token: localStorage.getItem("recipe_token"),
  user: JSON.parse(localStorage.getItem("recipe_user") || "null"),
  ingredients: [],
  recipes: [],
  recommendations: [],
  summary: null,
  editingIngredientId: null,
};

const $ = (selector) => document.querySelector(selector);

const authView = $("#auth-view");
const appView = $("#app-view");
const toast = $("#toast");
const sessionLabel = $("#session-label");
const logoutButton = $("#logout-button");
const ingredientForm = $("#ingredient-form");
const generatorForm = $("#generator-form");
const saveIngredientButton = $("#save-ingredient-button");
const cancelEditButton = $("#cancel-edit-button");
const generateButton = $("#generate-button");
const recipeSearch = $("#recipe-search");
const favoritesOnly = $("#favorites-only");
const pantryProducts = [
  "Arroz", "Huevos", "Tomate", "Cebolla", "Papa", "Yuca", "Platano", "Arepa",
  "Pan", "Pasta", "Queso", "Leche", "Avena", "Frijol", "Lenteja", "Garbanzo",
  "Pollo", "Carne", "Cerdo", "Pescado", "Atun", "Zanahoria", "Repollo",
  "Pepino", "Pimenton", "Ajo", "Cilantro", "Lechuga", "Maiz", "Aguacate",
  "Banano", "Manzana", "Naranja", "Limon", "Panela", "Chocolate", "Cafe"
];

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.style.background = isError ? "#a32929" : "#20231f";
  toast.classList.remove("hidden");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.add("hidden"), 3200);
}

function setSession(token, user) {
  state.token = token;
  state.user = user;
  if (token) {
    localStorage.setItem("recipe_token", token);
    localStorage.setItem("recipe_user", JSON.stringify(user));
  } else {
    localStorage.removeItem("recipe_token");
    localStorage.removeItem("recipe_user");
  }
  renderSession();
}

function renderSession() {
  const signedIn = Boolean(state.token);
  authView.classList.toggle("hidden", signedIn);
  appView.classList.toggle("hidden", !signedIn);
  logoutButton.classList.toggle("hidden", !signedIn);
  sessionLabel.textContent = signedIn ? state.user.email : "Sin sesion";
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }
  const response = await fetch(path, { ...options, headers });
  if (response.status === 204) {
    return null;
  }
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || "No fue posible completar la solicitud");
  }
  return payload;
}

function formPayload(form) {
  return Object.fromEntries(new FormData(form).entries());
}

async function submitAuth(event, path) {
  event.preventDefault();
  const button = event.currentTarget.querySelector("button[type='submit']");
  button.disabled = true;
  try {
    const payload = formPayload(event.currentTarget);
    const data = await api(path, { method: "POST", body: JSON.stringify(payload) });
    setSession(data.access_token, data.user);
    event.currentTarget.reset();
    await loadAll();
    showToast("Sesion iniciada");
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.disabled = false;
  }
}

async function loadAll() {
  if (!state.token) return;
  const [ingredients, recipes, summary] = await Promise.all([
    api("/api/ingredients"),
    api("/api/recipes"),
    api("/api/ingredients/summary"),
  ]);
  state.ingredients = ingredients;
  state.recipes = recipes;
  state.summary = summary;
  state.recommendations = await api("/api/recipes/recommendations");
  renderDashboard();
  renderIngredients();
  renderRecommendations();
  renderRecipes();
}

function renderDashboard() {
  $("#metric-items").textContent = state.ingredients.length;
  $("#metric-score").textContent = `${state.summary?.inventory_score || 0}%`;
  $("#metric-recipes").textContent = state.recipes.length;
  $("#metric-favorites").textContent = state.recipes.filter((recipe) => recipe.is_favorite).length;
  $("#ingredient-count").textContent = state.ingredients.length;

  const insights = $("#inventory-insights");
  insights.innerHTML = (state.summary?.suggestions || [])
    .map((item) => `<div class="insight">${escapeHtml(item)}</div>`)
    .join("");
}

function renderIngredients() {
  renderQuickPantry();
  const list = $("#ingredients-list");
  if (!state.ingredients.length) {
    list.innerHTML = `<p class="empty">Agrega lo que tienes en casa para activar el generador.</p>`;
    return;
  }
  list.innerHTML = state.ingredients
    .map(
      (item) => `
        <article class="ingredient-item">
          <p class="ingredient-main">${escapeHtml(item.name)}</p>
          <p class="ingredient-meta">${Number(item.quantity).toLocaleString()} ${escapeHtml(item.unit)}${item.notes ? ` · ${escapeHtml(item.notes)}` : ""}</p>
          <div class="item-actions">
            <button class="ghost" type="button" data-edit-ingredient="${item.id}">Editar</button>
            <button class="danger" type="button" data-delete-ingredient="${item.id}">Eliminar</button>
          </div>
        </article>
      `
    )
    .join("");
}

function renderQuickPantry() {
  const list = $("#quick-pantry-list");
  const existing = new Set(state.ingredients.map((item) => item.name.toLowerCase()));
  list.innerHTML = pantryProducts
    .map((name) => {
      const active = existing.has(name.toLowerCase());
      return `<button class="quick-chip ${active ? "active" : ""}" type="button" data-quick-product="${escapeHtml(name)}">${escapeHtml(name)}</button>`;
    })
    .join("");
}

function filteredRecipes() {
  const query = recipeSearch.value.trim().toLowerCase();
  return state.recipes.filter((recipe) => {
    const matchesText = !query || [
      recipe.name,
      recipe.description,
      ...(recipe.tags || []),
    ].join(" ").toLowerCase().includes(query);
    const matchesFavorite = !favoritesOnly.checked || recipe.is_favorite;
    return matchesText && matchesFavorite;
  });
}

function renderRecipes() {
  const list = $("#recipes-list");
  const recipes = filteredRecipes();
  if (!recipes.length) {
    list.innerHTML = `<p class="empty">No hay recetas para mostrar con esos filtros.</p>`;
    return;
  }
  list.innerHTML = recipes.map(renderRecipeCard).join("");
}

function renderRecommendations() {
  const list = $("#recommendations-list");
  if (!state.recommendations.length) {
    list.innerHTML = `<p class="empty">Agrega mas ingredientes para recibir recomendaciones utiles.</p>`;
    return;
  }
  list.innerHTML = state.recommendations
    .map(
      (item) => `
        <article class="recommendation-card">
          <div class="recommendation-score">${item.match_score}%</div>
          <div>
            <h3>${escapeHtml(item.title)}</h3>
            <p>${escapeHtml(item.description)}</p>
          </div>
          <div class="chips">
            ${(item.tags || []).map((tag) => `<span class="chip wine">${escapeHtml(tag)}</span>`).join("")}
          </div>
          <p class="recommendation-reason">${escapeHtml(item.reason)}</p>
          ${renderCompactBreakdown(item.breakdown)}
          <button type="button" data-generate-recommendation="${escapeHtml(item.title)}">Generar esta receta</button>
        </article>
      `
    )
    .join("");
}

function renderRecipeCard(recipe) {
  const tags = (recipe.tags || [])
    .map((tag) => `<span class="chip">${escapeHtml(tag)}</span>`)
    .join("");
  const missing = (recipe.missing_ingredients || [])
    .map((item) => `<span class="chip warning">${escapeHtml(item)}</span>`)
    .join("");
  const nutrition = Object.entries(recipe.nutrition || {})
    .map(
      ([key, value]) => `
        <span>${escapeHtml(labelize(key))}<strong>${escapeHtml(value)}</strong></span>
      `
    )
    .join("");
  const tips = (recipe.tips || [])
    .map((tip) => `<li>${escapeHtml(tip)}</li>`)
    .join("");
  return `
    <article class="recipe-card">
      <img class="recipe-photo" src="/static/images/recipe-default.jpg" alt="Foto de receta casera generada">
      <div class="recipe-head">
        <div>
          <h3>${escapeHtml(recipe.name)}</h3>
          <p class="recipe-meta">${escapeHtml(recipe.estimated_time)} · ${escapeHtml(recipe.difficulty)} · ${recipe.servings} porciones</p>
        </div>
        <button class="favorite-button ${recipe.is_favorite ? "active" : ""}" type="button" data-favorite-recipe="${recipe.id}">
          ${recipe.is_favorite ? "Favorita" : "Marcar fav"}
        </button>
      </div>
      ${recipe.description ? `<p class="description">${escapeHtml(recipe.description)}</p>` : ""}
      ${tags || missing ? `<div class="chips">${tags}${missing}</div>` : ""}
      <div>
        <strong>Ingredientes</strong>
        <ul>${recipe.ingredients
          .map((item) => `<li>${escapeHtml(item.name)}: ${escapeHtml(item.quantity)}</li>`)
          .join("")}</ul>
      </div>
      ${renderBreakdown(recipeBreakdown(recipe))}
      <div>
        <strong>Preparacion</strong>
        <ol>${recipe.steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ol>
      </div>
      ${nutrition ? `<div class="nutrition">${nutrition}</div>` : ""}
      ${tips ? `<div><strong>Consejos del chef</strong><ul>${tips}</ul></div>` : ""}
      <div class="rating-row">
        <select data-rate-recipe="${recipe.id}" aria-label="Calificar receta">
          <option value="">${recipe.rating ? `${recipe.rating.score} estrellas` : "Calificar"}</option>
          <option value="1">1 estrella</option>
          <option value="2">2 estrellas</option>
          <option value="3">3 estrellas</option>
          <option value="4">4 estrellas</option>
          <option value="5">5 estrellas</option>
        </select>
        <button class="ghost" type="button" data-copy-recipe="${recipe.id}">Copiar</button>
        <button class="danger" type="button" data-delete-recipe="${recipe.id}">Eliminar</button>
      </div>
    </article>
  `;
}

function recipeBreakdown(recipe) {
  const inventoryNames = state.ingredients.map((item) => item.name.toLowerCase());
  const breakdown = (recipe.ingredients || []).map((item) => {
    const name = String(item.name || "").toLowerCase();
    const available = inventoryNames.some(
      (inventoryName) => name.includes(inventoryName) || inventoryName.includes(name)
    );
    return {
      name: item.name,
      status: available ? "disponible" : "faltante",
      detail: available ? item.quantity : "No aparece en inventario",
    };
  });
  for (const basic of ["aceite", "agua", "sal", "pimienta"]) {
    breakdown.push({ name: basic, status: "basico", detail: "Basico asumido" });
  }
  return breakdown;
}

function renderBreakdown(items) {
  if (!items?.length) return "";
  return `
    <div class="breakdown">
      <strong>Desglose de ingredientes</strong>
      <div class="breakdown-grid">
        ${items
          .map(
            (item) => `
              <span class="breakdown-item ${escapeHtml(item.status)}">
                <b>${escapeHtml(item.name)}</b>
                <small>${escapeHtml(item.status)} · ${escapeHtml(item.detail)}</small>
              </span>
            `
          )
          .join("")}
      </div>
    </div>
  `;
}

function renderCompactBreakdown(items) {
  const groups = {
    disponible: items.filter((item) => item.status === "disponible"),
    faltante: items.filter((item) => item.status === "faltante"),
    opcional: items.filter((item) => item.status === "opcional"),
    basico: items.filter((item) => item.status === "basico"),
  };
  return `
    <div class="compact-breakdown">
      ${compactGroup("Tengo", groups.disponible, "disponible")}
      ${compactGroup("Falta", groups.faltante, "faltante")}
      ${compactGroup("Opcional", groups.opcional.slice(0, 3), "opcional")}
      <p class="basics-note">${groups.basico.length} basicos asumidos: agua, sal, aceite y pimienta.</p>
    </div>
  `;
}

function compactGroup(label, items, status) {
  if (!items.length) {
    return status === "faltante"
      ? `<div><strong>${label}</strong><span class="mini-chip disponible">Nada clave</span></div>`
      : "";
  }
  return `
    <div>
      <strong>${label}</strong>
      <div class="mini-chip-row">
        ${items
          .map((item) => `<span class="mini-chip ${status}">${escapeHtml(item.name)}</span>`)
          .join("")}
      </div>
    </div>
  `;
}

function labelize(value) {
  return String(value).replaceAll("_", " ");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function resetIngredientForm() {
  state.editingIngredientId = null;
  ingredientForm.reset();
  ingredientForm.elements.unit.value = "unidad";
  saveIngredientButton.textContent = "Guardar";
  cancelEditButton.classList.add("hidden");
}

function generatorPayload() {
  const payload = formPayload(generatorForm);
  payload.servings = Number(payload.servings || 2);
  payload.max_time_minutes = Number(payload.max_time_minutes || 35);
  payload.strict_inventory = generatorForm.elements.strict_inventory.checked;
  for (const key of ["cuisine", "dietary_restrictions", "extra_instructions"]) {
    if (!payload[key]) {
      payload[key] = null;
    }
  }
  return payload;
}

ingredientForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  saveIngredientButton.disabled = true;
  const payload = formPayload(ingredientForm);
  payload.quantity = Number(payload.quantity);
  const path = state.editingIngredientId
    ? `/api/ingredients/${state.editingIngredientId}`
    : "/api/ingredients";
  const method = state.editingIngredientId ? "PUT" : "POST";
  try {
    await api(path, { method, body: JSON.stringify(payload) });
    resetIngredientForm();
    await loadAll();
    showToast("Ingrediente guardado");
  } catch (error) {
    showToast(error.message, true);
  } finally {
    saveIngredientButton.disabled = false;
  }
});

generatorForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  generateButton.disabled = true;
  generateButton.textContent = "Generando receta...";
  try {
    await api("/api/recipes/generate", {
      method: "POST",
      body: JSON.stringify(generatorPayload()),
    });
    await loadAll();
    showToast("Receta generada con preferencias");
  } catch (error) {
    showToast(error.message, true);
  } finally {
    generateButton.disabled = false;
    generateButton.textContent = "Generar receta IA";
  }
});

cancelEditButton.addEventListener("click", resetIngredientForm);
recipeSearch.addEventListener("input", renderRecipes);
favoritesOnly.addEventListener("change", renderRecipes);

document.addEventListener("click", async (event) => {
  const editId = event.target.dataset.editIngredient;
  const deleteIngredientId = event.target.dataset.deleteIngredient;
  const deleteRecipeId = event.target.dataset.deleteRecipe;
  const favoriteRecipeId = event.target.dataset.favoriteRecipe;
  const copyRecipeId = event.target.dataset.copyRecipe;
  const recommendationTitle = event.target.dataset.generateRecommendation;
  const quickProduct = event.target.dataset.quickProduct;

  try {
    if (editId) {
      const ingredient = state.ingredients.find((item) => item.id === Number(editId));
      if (!ingredient) return;
      state.editingIngredientId = ingredient.id;
      ingredientForm.elements.name.value = ingredient.name;
      ingredientForm.elements.quantity.value = ingredient.quantity;
      ingredientForm.elements.unit.value = ingredient.unit;
      ingredientForm.elements.notes.value = ingredient.notes || "";
      saveIngredientButton.textContent = "Actualizar";
      cancelEditButton.classList.remove("hidden");
    }

    if (deleteIngredientId) {
      await api(`/api/ingredients/${deleteIngredientId}`, { method: "DELETE" });
      await loadAll();
      showToast("Ingrediente eliminado");
    }

    if (deleteRecipeId) {
      await api(`/api/recipes/${deleteRecipeId}`, { method: "DELETE" });
      await loadAll();
      showToast("Receta eliminada");
    }

    if (favoriteRecipeId) {
      const recipe = state.recipes.find((item) => item.id === Number(favoriteRecipeId));
      await api(`/api/recipes/${favoriteRecipeId}/favorite`, {
        method: "PATCH",
        body: JSON.stringify({ is_favorite: !recipe?.is_favorite }),
      });
      await loadAll();
      showToast("Favorito actualizado");
    }

    if (copyRecipeId) {
      const recipe = state.recipes.find((item) => item.id === Number(copyRecipeId));
      await navigator.clipboard.writeText(recipeToText(recipe));
      showToast("Receta copiada al portapapeles");
    }

    if (recommendationTitle) {
      generatorForm.elements.extra_instructions.value = `Genera especificamente: ${recommendationTitle}. Explica bien el desglose de ingredientes.`;
      generatorForm.requestSubmit();
    }

    if (quickProduct) {
      const exists = state.ingredients.some(
        (item) => item.name.toLowerCase() === quickProduct.toLowerCase()
      );
      if (exists) {
        showToast("Ese producto ya esta en el inventario");
        return;
      }
      await api("/api/ingredients", {
        method: "POST",
        body: JSON.stringify({
          name: quickProduct,
          quantity: 1,
          unit: "unidad",
          notes: "agregado desde canasta familiar",
        }),
      });
      await loadAll();
      showToast("Producto de canasta agregado");
    }
  } catch (error) {
    showToast(error.message, true);
  }
});

document.addEventListener("change", async (event) => {
  const recipeId = event.target.dataset.rateRecipe;
  if (!recipeId || !event.target.value) return;
  try {
    await api(`/api/recipes/${recipeId}/ratings`, {
      method: "POST",
      body: JSON.stringify({ score: Number(event.target.value) }),
    });
    await loadAll();
    showToast("Calificacion guardada");
  } catch (error) {
    showToast(error.message, true);
  }
});

function recipeToText(recipe) {
  if (!recipe) return "";
  const ingredients = recipe.ingredients
    .map((item) => `- ${item.name}: ${item.quantity}`)
    .join("\n");
  const steps = recipe.steps.map((step, index) => `${index + 1}. ${step}`).join("\n");
  return `${recipe.name}\n${recipe.description || ""}\n\nIngredientes:\n${ingredients}\n\nPreparacion:\n${steps}`;
}

$("#login-form").addEventListener("submit", (event) =>
  submitAuth(event, "/api/auth/login")
);
$("#register-form").addEventListener("submit", (event) =>
  submitAuth(event, "/api/auth/register")
);
logoutButton.addEventListener("click", () => {
  setSession(null, null);
  state.ingredients = [];
  state.recipes = [];
  state.summary = null;
  resetIngredientForm();
  showToast("Sesion cerrada");
});

renderSession();
if (state.token) {
  loadAll().catch((error) => {
    setSession(null, null);
    showToast(error.message, true);
  });
}

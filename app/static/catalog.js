// Trellis catalog page behavior.
//
// Two deliberate timing hazards live here:
//   1. Search results replace the list only after the (slow) API answers.
//   2. The "featured plant" banner renders ~800ms after page load.
// Browser tests must survive both without a single sleep() call.

async function runSearch() {
  const q = document.getElementById("search-box").value;
  const category = document.getElementById("category-filter").value;
  const inStock = document.getElementById("in-stock-only").checked ? "1" : "";
  const status = document.getElementById("search-status");
  const list = document.getElementById("plant-list");

  status.textContent = "Searching…";
  const params = new URLSearchParams({ q, category, in_stock: inStock });
  const resp = await fetch(`/api/search?${params}`);
  const data = await resp.json();

  list.innerHTML = "";
  for (const p of data.results) {
    const li = document.createElement("li");
    li.className = "card";
    li.dataset.testid = `plant-${p.id}`;
    li.innerHTML = `
      <strong>${p.name}</strong>
      <span class="meta">${p.category} · $${p.price.toFixed(2)}</span>
      ${p.in_stock
        ? `<form method="post" action="/cart/add/${p.id}">
             <button type="submit" data-testid="add-${p.id}">Add to cart</button>
           </form>`
        : `<button disabled data-testid="add-${p.id}">Out of stock</button>`}
    `;
    list.appendChild(li);
  }
  status.textContent = data.count === 0
    ? "No plants matched."
    : `${data.count} plant${data.count === 1 ? "" : "s"} found.`;
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("search-button").addEventListener("click", runSearch);

  // Late-rendering element: simulates a recommendation widget arriving after
  // the rest of the page. Tests that grab the DOM too early never see it.
  setTimeout(() => {
    const slot = document.getElementById("featured-slot");
    const div = document.createElement("div");
    div.className = "featured";
    div.dataset.testid = "featured-plant";
    div.textContent = "🌱 Featured today: Fiddlehead Fern — unfurling slowly, like all good things.";
    slot.appendChild(div);
  }, 800);
});

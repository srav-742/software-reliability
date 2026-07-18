/**
 * Helper utility to parse raw string or JSON recommendations into structured
 * recommendation cards with category, action, impact, severity, and code snippets.
 */

export function parseRecommendation(rawRec) {
  if (!rawRec) return null;

  // Handle object input
  if (typeof rawRec === 'object' && rawRec !== null) {
    return {
      category: rawRec.category || rawRec.title || 'Code Optimization',
      action: rawRec.action || rawRec.description || 'Refactor long methods.',
      impact: rawRec.impact || '+0.25',
      severity: rawRec.severity || 'Medium',
      detail: rawRec.detail || 'High risk metric observed during automated analysis.',
      codeTip: rawRec.codeTip || '// Recommended Refactoring\n// Break long methods into smaller pure helper functions',
      tags: rawRec.tags || ['Refactoring', 'Maintainability'],
    };
  }

  const str = String(rawRec).trim();

  // Handle raw JSON string
  if (str.startsWith('{') && str.endsWith('}')) {
    try {
      const parsed = JSON.parse(str);
      return parseRecommendation(parsed);
    } catch {
      // Fallback if parsing fails
    }
  }

  // Check for SHAP impact bracket like [+0.42] or [+0.26]
  let impact = '+0.20';
  let cleanStr = str;

  const bracketMatch = str.match(/^\[([+\-]?\d+(?:\.\d+)?%?(?:\s*risk\s*impact)?)\]\s*(.*)/i);
  if (bracketMatch) {
    impact = bracketMatch[1].includes('+') || bracketMatch[1].includes('-')
      ? bracketMatch[1]
      : `+${bracketMatch[1]}`;
    cleanStr = bracketMatch[2];
  }

  // Handle "Category: Action" split
  let category = 'High Complexity';
  let action = cleanStr;

  if (cleanStr.includes(':')) {
    const parts = cleanStr.split(':');
    category = parts[0].trim();
    action = parts.slice(1).join(':').trim();
  } else {
    // Infer category from content keywords
    const lower = cleanStr.toLowerCase();
    if (lower.includes('nested') || lower.includes('depth')) {
      category = 'Nested Logic';
      action = 'Reduce nested conditions.';
    } else if (lower.includes('query') || lower.includes('database') || lower.includes('sql')) {
      category = 'Database Queries';
      action = 'Optimize SQL queries.';
    } else if (lower.includes('complex') || lower.includes('method') || lower.includes('cyclomatic')) {
      category = 'High Complexity';
      action = 'Refactor long methods.';
    } else if (lower.includes('duplicate') || lower.includes('copy')) {
      category = 'Duplicate Code';
      action = 'Eliminate duplicate code using shared helper functions.';
    } else if (lower.includes('line') || lower.includes('loc') || lower.includes('monolith')) {
      category = 'High LOC';
      action = 'Break down monolithic files into smaller modules.';
    } else if (lower.includes('cpu')) {
      category = 'CPU Overhead';
      action = 'Offload heavy computations to background workers.';
    } else if (lower.includes('memory')) {
      category = 'Memory Footprint';
      action = 'Use lazy loading and generators to reduce RAM allocations.';
    } else if (lower.includes('import') || lower.includes('dependency')) {
      category = 'Imports & Dependencies';
      action = 'Clean unused imports and resolve circular references.';
    }
  }

  // Assign default code tip and severity based on category
  let severity = 'High';
  let codeTip = '// Recommended Refactoring\n// Break long methods into smaller pure helper functions';

  const catLower = category.toLowerCase();
  if (catLower.includes('nest')) {
    severity = 'High';
    codeTip = `// Before:\nif (isAvailable) {\n  if (hasPermission) {\n    executeTask();\n  }\n}\n\n// After (Guard Clause):\nif (!isAvailable || !hasPermission) return;\nexecuteTask();`;
  } else if (catLower.includes('query') || catLower.includes('database')) {
    severity = 'Critical';
    codeTip = `-- Before:\nSELECT * FROM users WHERE status = 'active'; -- Missing Index\n\n-- After:\nCREATE INDEX idx_users_status ON users(status);\nSELECT id, email FROM users WHERE status = 'active';`;
  } else if (catLower.includes('complex')) {
    severity = 'High';
    codeTip = `// Before: Single 150-line method\nfunction processOrder(order) { /* 150 lines */ }\n\n// After: Single Responsibility Principle\nfunction processOrder(order) {\n  validateOrder(order);\n  calculateTax(order);\n  persistOrder(order);\n}`;
  } else if (catLower.includes('dup')) {
    severity = 'Medium';
    codeTip = `// Extract duplicate logic into a shared utility\nexport const sanitizeInput = (val) => val.trim().toLowerCase();`;
  } else if (catLower.includes('loc')) {
    severity = 'Medium';
    codeTip = `// Split large file into modular sub-modules:\n// - src/services/userAuth.js\n// - src/services/userProfile.js`;
  }

  return {
    category,
    action,
    impact,
    severity,
    detail: `SHAP feature attribution identified '${category}' as a primary risk driver (${impact} probability impact).`,
    codeTip,
    tags: [category, severity],
  };
}

export const storage = {
  get: (key) => {
    if (typeof window === 'undefined') return null;
    try {
      const item = window.localStorage.getItem(key);
      if (!item) return null;
      
      // Handle both string and object values
      try {
        return JSON.parse(item);
      } catch (parseError) {
        // If parsing fails, return the raw string
        return item;
      }
    } catch (error) {
      console.error(`Error reading ${key} from localStorage:`, error);
      return null;
    }
  },

  set: (key, value) => {
    if (typeof window === 'undefined') return;
    try {
      // Ensure we're storing a string
      const serializedValue = typeof value === 'string' ? value : JSON.stringify(value);
      window.localStorage.setItem(key, serializedValue);
    } catch (error) {
      console.error(`Error saving ${key} to localStorage:`, error);
    }
  },

  remove: (key) => {
    if (typeof window === 'undefined') return;
    try {
      window.localStorage.removeItem(key);
    } catch (error) {
      console.error(`Error removing ${key} from localStorage:`, error);
    }
  }
}; 
import { createContext, useState, useContext } from 'react';

// 1. Create a Context
const DataContext = createContext();

// 2. Create a Provider Component (This wraps the app)
export function DataProvider({ children }) {
  const [sharedData, setSharedData] = useState("Hello from Context!");

  return (
    <DataContext.Provider value={{ sharedData, setSharedData }}>
      {children} {/* All components inside this will have access to the context */}
    </DataContext.Provider>
  );
}

// 3. Create a Custom Hook to Use Context
export function useData() {
  return useContext(DataContext);
}

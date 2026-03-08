import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

/**
 * Example demonstrating React Query usage patterns.
 * Replace with actual API calls when implementing features.
 */

interface ExampleItem {
  id: number;
  name: string;
}

// Simulated API functions (replace with actual fetch calls)
const fetchExamples = async (): Promise<ExampleItem[]> => {
  // In production: return fetch('/api/v1/examples').then(res => res.json())
  return [
    { id: 1, name: 'Example 1' },
    { id: 2, name: 'Example 2' },
  ];
};

const createExample = async (name: string): Promise<ExampleItem> => {
  // In production: return fetch('/api/v1/examples', { method: 'POST', body: JSON.stringify({ name }) }).then(res => res.json())
  return { id: Date.now(), name };
};

// Query hook for fetching data
export function useExamples() {
  return useQuery({
    queryKey: ['examples'],
    queryFn: fetchExamples,
  });
}

// Mutation hook for creating data
export function useCreateExample() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createExample,
    onSuccess: () => {
      // Invalidate and refetch examples after successful mutation
      queryClient.invalidateQueries({ queryKey: ['examples'] });
    },
  });
}

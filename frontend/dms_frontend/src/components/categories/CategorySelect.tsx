import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { categoryService } from '../../services/categories';

interface CategorySelectProps {
  value?: number;
  onChange: (categoryId: number) => void;
  className?: string;
}

export const CategorySelect: React.FC<CategorySelectProps> = ({ value, onChange, className }) => {
  const { data: categories, isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: categoryService.getCategories,
  });

  if (isLoading) {
    return <select disabled className={className}>
      <option>Loading categories...</option>
    </select>;
  }

  return (
    <select
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      className={`w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${className}`}
    >
      <option value="">All Categories</option>
      {categories?.map((category) => (
        <option key={category.id} value={category.id}>
          {category.name}
        </option>
      ))}
    </select>
  );
};

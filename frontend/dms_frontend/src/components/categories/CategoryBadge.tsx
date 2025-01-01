import React from 'react';
import { Category } from '../../types/category';

interface CategoryBadgeProps {
  category: Category;
  onRemove?: () => void;
}

export const CategoryBadge: React.FC<CategoryBadgeProps> = ({ category, onRemove }) => {
  return (
    <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
      {category.name}
      {onRemove && (
        <button
          type="button"
          className="ml-1 inline-flex items-center rounded-full text-blue-700 hover:bg-blue-100 focus:outline-none"
          onClick={onRemove}
        >
          <span className="sr-only">Remove category {category.name}</span>
          ×
        </button>
      )}
    </span>
  );
};

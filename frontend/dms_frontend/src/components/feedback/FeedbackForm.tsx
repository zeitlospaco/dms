import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { CategorySelect } from '@/components/categories/CategorySelect';
import { toast } from '@/hooks/use-toast';
import { feedbackService } from '@/services/feedback';

interface FeedbackFormProps {
  documentId: number;
  currentCategory: string;
  onFeedbackSubmitted?: () => void;
}

export const FeedbackForm: React.FC<FeedbackFormProps> = ({ 
  documentId, 
  currentCategory, 
  onFeedbackSubmitted 
}) => {
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | undefined>();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmitFeedback = async () => {
    if (isCorrect === false && !selectedCategoryId) {
      toast({
        title: 'Error',
        description: 'Please select the correct category',
        variant: 'destructive',
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await feedbackService.submitFeedback({
        document_id: documentId,
        correct_category: isCorrect ? currentCategory : String(selectedCategoryId),
        comment: isCorrect ? 'Correct categorization' : 'Incorrect categorization',
      });

      toast({
        title: 'Success',
        description: 'Thank you for your feedback!',
      });

      onFeedbackSubmitted?.();
      setIsCorrect(null);
      setSelectedCategoryId(undefined);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      toast({
        title: 'Error',
        description: 'Failed to submit feedback. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium">Was this categorization correct?</h3>
      
      <div className="space-x-2">
        <Button
          variant={isCorrect === true ? 'default' : 'outline'}
          onClick={() => setIsCorrect(true)}
          disabled={isSubmitting}
        >
          Yes
        </Button>
        <Button
          variant={isCorrect === false ? 'default' : 'outline'}
          onClick={() => setIsCorrect(false)}
          disabled={isSubmitting}
        >
          No
        </Button>
      </div>

      {isCorrect === false && (
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">Please select the correct category:</p>
          <CategorySelect
            value={selectedCategoryId}
            onChange={setSelectedCategoryId}
            disabled={isSubmitting}
            className="w-full"
          />
        </div>
      )}

      {isCorrect !== null && (
        <Button
          onClick={handleSubmitFeedback}
          disabled={isSubmitting}
          className="w-full mt-4"
        >
          {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
        </Button>
      )}
    </div>
  );
};

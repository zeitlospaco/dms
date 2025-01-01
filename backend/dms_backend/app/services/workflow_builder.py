from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Document, User, WorkflowTemplate, WorkflowStep, WorkflowInstance
import json
import logging

class WorkflowBuilderService:
    def __init__(self, db: Session):
        self.db = db

    async def create_workflow_template(
        self,
        name: str,
        description: str,
        steps: List[Dict],
        created_by: str
    ) -> WorkflowTemplate:
        """Create a new workflow template"""
        try:
            template = WorkflowTemplate(
                name=name,
                description=description,
                created_by=created_by,
                steps=json.dumps(steps),
                created_at=datetime.utcnow()
            )
            
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            return template
            
        except Exception as e:
            logging.error(f"Error creating workflow template: {str(e)}")
            self.db.rollback()
            raise

    async def get_workflow_templates(self, user_id: str) -> List[WorkflowTemplate]:
        """Get all workflow templates accessible to the user"""
        return self.db.query(WorkflowTemplate)\
            .filter(
                WorkflowTemplate.created_by == user_id
            ).all()

    async def start_workflow(
        self,
        template_id: int,
        document_id: str,
        initiator_id: str
    ) -> WorkflowInstance:
        """Start a new workflow instance from a template"""
        try:
            template = self.db.query(WorkflowTemplate)\
                .filter(WorkflowTemplate.id == template_id)\
                .first()
            
            if not template:
                raise ValueError(f"Workflow template {template_id} not found")

            # Create workflow instance
            instance = WorkflowInstance(
                template_id=template_id,
                document_id=document_id,
                initiator_id=initiator_id,
                status='active',
                current_step=0,
                started_at=datetime.utcnow()
            )
            
            self.db.add(instance)
            
            # Create initial workflow step
            steps = json.loads(template.steps)
            if steps:
                first_step = steps[0]
                step = WorkflowStep(
                    workflow_instance_id=instance.id,
                    step_number=0,
                    assignee_id=first_step['assignee_id'],
                    action_required=first_step['action'],
                    deadline=datetime.utcnow() + timedelta(days=first_step.get('deadline_days', 7)),
                    status='pending'
                )
                self.db.add(step)

            self.db.commit()
            self.db.refresh(instance)
            return instance

        except Exception as e:
            logging.error(f"Error starting workflow: {str(e)}")
            self.db.rollback()
            raise

    async def complete_workflow_step(
        self,
        instance_id: int,
        step_number: int,
        user_id: str,
        action: str,
        comments: Optional[str] = None
    ) -> WorkflowInstance:
        """Complete a workflow step and advance to the next step"""
        try:
            instance = self.db.query(WorkflowInstance)\
                .filter(WorkflowInstance.id == instance_id)\
                .first()
            
            if not instance or instance.status != 'active':
                raise ValueError("Invalid workflow instance")

            current_step = self.db.query(WorkflowStep)\
                .filter(and_(
                    WorkflowStep.workflow_instance_id == instance_id,
                    WorkflowStep.step_number == step_number
                )).first()
            
            if not current_step or current_step.status != 'pending':
                raise ValueError("Invalid workflow step")

            if current_step.assignee_id != user_id:
                raise ValueError("User not authorized to complete this step")

            # Update current step
            current_step.status = 'completed'
            current_step.completed_at = datetime.utcnow()
            current_step.action_taken = action
            current_step.comments = comments

            # Get workflow template
            template = self.db.query(WorkflowTemplate)\
                .filter(WorkflowTemplate.id == instance.template_id)\
                .first()
            
            steps = json.loads(template.steps)
            
            # Check if there are more steps
            if step_number + 1 < len(steps):
                # Create next step
                next_step_data = steps[step_number + 1]
                next_step = WorkflowStep(
                    workflow_instance_id=instance_id,
                    step_number=step_number + 1,
                    assignee_id=next_step_data['assignee_id'],
                    action_required=next_step_data['action'],
                    deadline=datetime.utcnow() + timedelta(days=next_step_data.get('deadline_days', 7)),
                    status='pending'
                )
                self.db.add(next_step)
                instance.current_step = step_number + 1
            else:
                # Complete workflow
                instance.status = 'completed'
                instance.completed_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(instance)
            return instance

        except Exception as e:
            logging.error(f"Error completing workflow step: {str(e)}")
            self.db.rollback()
            raise

    async def get_pending_tasks(self, user_id: str) -> List[Dict]:
        """Get all pending workflow tasks assigned to a user"""
        try:
            pending_steps = self.db.query(WorkflowStep)\
                .join(WorkflowInstance)\
                .filter(and_(
                    WorkflowStep.assignee_id == user_id,
                    WorkflowStep.status == 'pending',
                    WorkflowInstance.status == 'active'
                )).all()

            tasks = []
            for step in pending_steps:
                instance = self.db.query(WorkflowInstance)\
                    .filter(WorkflowInstance.id == step.workflow_instance_id)\
                    .first()
                
                document = self.db.query(Document)\
                    .filter(Document.id == instance.document_id)\
                    .first()

                template = self.db.query(WorkflowTemplate)\
                    .filter(WorkflowTemplate.id == instance.template_id)\
                    .first()

                tasks.append({
                    'task_id': step.id,
                    'workflow_name': template.name,
                    'document_name': document.name if document else "Unknown",
                    'action_required': step.action_required,
                    'deadline': step.deadline,
                    'workflow_instance_id': instance.id,
                    'step_number': step.step_number
                })

            return tasks

        except Exception as e:
            logging.error(f"Error getting pending tasks: {str(e)}")
            return []

    async def get_workflow_history(self, document_id: str) -> List[Dict]:
        """Get workflow history for a document"""
        try:
            instances = self.db.query(WorkflowInstance)\
                .filter(WorkflowInstance.document_id == document_id)\
                .all()

            history = []
            for instance in instances:
                template = self.db.query(WorkflowTemplate)\
                    .filter(WorkflowTemplate.id == instance.template_id)\
                    .first()

                steps = self.db.query(WorkflowStep)\
                    .filter(WorkflowStep.workflow_instance_id == instance.id)\
                    .order_by(WorkflowStep.step_number)\
                    .all()

                history.append({
                    'workflow_id': instance.id,
                    'workflow_name': template.name,
                    'status': instance.status,
                    'started_at': instance.started_at,
                    'completed_at': instance.completed_at,
                    'steps': [
                        {
                            'step_number': step.step_number,
                            'action_required': step.action_required,
                            'assignee_id': step.assignee_id,
                            'status': step.status,
                            'completed_at': step.completed_at,
                            'action_taken': step.action_taken,
                            'comments': step.comments
                        }
                        for step in steps
                    ]
                })

            return history

        except Exception as e:
            logging.error(f"Error getting workflow history: {str(e)}")
            return []

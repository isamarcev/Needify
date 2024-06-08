from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.apps.tasks.enums import TaskStatusEnum
from src.apps.tasks.schemas import TaskSchema


@dataclass
class BusinessRule(ABC):
    @abstractmethod
    def is_broken(self, *args, **kwargs) -> bool:
        pass


@dataclass
class ChangeStatusTaskRule(BusinessRule):
    task_to_update: TaskSchema
    new_status: TaskStatusEnum
    action_by_user_id: int

    def is_broken(self) -> bool:
        if (self.action_by_user_id != self.task_to_update.poster_id) and (
            self.action_by_user_id != self.task_to_update.doer_id
        ):
            raise ValueError("Only customer or doer can change task status")

        match self.action_by_user_id:
            case self.task_to_update.poster_id:
                route_mapping = TaskStatusEnum.mapping_rules_to_update_by_customer()
                if self.task_to_update.status.value not in route_mapping.keys():
                    raise ValueError("Customer cannot change task status")
                if self.new_status not in route_mapping[self.task_to_update.status.value]:
                    raise ValueError("Customer cannot change task status to this value")
                return False
            case self.task_to_update.doer_id:
                route_mapping = TaskStatusEnum.mapping_rules_to_update_by_doer()
                if self.task_to_update.status.value not in route_mapping.keys():
                    raise ValueError("Doer cannot change task status")
                if self.new_status not in route_mapping[self.task_to_update.status.value]:
                    raise ValueError("Doer cannot change task status to this value")
                return False
        return True

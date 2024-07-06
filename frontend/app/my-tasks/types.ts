import { ITaskRaw } from '@/services/types';
import { ITaskShortCard } from '@/widgets/TaskCard/types';

export interface IUserRawTasks {
  published_tasks: ITaskRaw[] | null;
  picked_up_tasks: ITaskRaw[] | null;
  completed_tasks: ITaskRaw[] | null;
}

export interface IUserTasks {
  published_tasks: ITaskShortCard[];
  picked_up_tasks: ITaskShortCard[];
  completed_tasks: ITaskShortCard[];
}

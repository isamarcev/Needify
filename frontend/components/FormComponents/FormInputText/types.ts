import { IFormInputProps } from '@/components/FormComponents/types';
import { ICreateTaskValues } from '@/app/create-task/types';

export interface IFormInputText extends IFormInputProps<ICreateTaskValues> {
  multiline?: boolean;
  rows?: number;
}

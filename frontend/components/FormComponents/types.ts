import { Control, FieldValues } from 'react-hook-form';

export interface IFormInputProps<T extends FieldValues> {
  name: string;
  control: Control<T>;
  label?: string;
  className?: string;
}

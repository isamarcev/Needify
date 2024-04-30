export interface ISelector<T = string> {
  label: string;
  defaultValue?: string;
  options: T[];
  onChange: (value: T) => void;
}

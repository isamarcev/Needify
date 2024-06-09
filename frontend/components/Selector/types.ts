export interface ISelector {
  label: string;
  defaultValue?: string;
  options: IOption[];
  onChange: (value: string) => void;
}

export interface IOption {
  id: string;
  label: string;
}

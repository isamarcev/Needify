import { FC, useCallback, useState } from 'react';
import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
} from '@mui/material';
import { ISelector } from '@/components/Selector/types';

export const Selector: FC<ISelector> = ({
  onChange,
  options,
  label,
  defaultValue,
}) => {
  const [value, setValue] = useState<string>(defaultValue ?? '');

  const handleChange = useCallback(
    (event: SelectChangeEvent) => {
      const { value } = event.target;
      setValue(value);
      onChange(value);
    },
    [onChange],
  );

  return (
    <FormControl fullWidth variant="outlined">
      <InputLabel id={`${label}-label`}>{label}</InputLabel>
      <Select
        labelId={`${label}-label`}
        id={label}
        value={value}
        label={label}
        onChange={handleChange}
      >
        {options.map(({ id, label }) => (
          <MenuItem key={id} value={label}>
            {label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

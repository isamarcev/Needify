import { FC, useCallback, useState } from 'react';
import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
} from '@mui/material';
import { ISelector } from '@/components/Selector/types';
import styles from './Selector.module.css';

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
    <FormControl fullWidth variant="filled">
      <InputLabel id={`${label}-label`}>{label}</InputLabel>
      <Select
        className={styles.selector}
        labelId={`${label}-label`}
        id={label}
        value={value}
        label={label}
        onChange={handleChange}
      >
        {options.map(({ id, label }) => (
          <MenuItem key={id} value={label} className={styles.menuItem}>
            {label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

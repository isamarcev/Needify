import { FC, useCallback, useState } from 'react';
import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
} from '@mui/material';
import styles from './selector.module.css';
import { ISelector } from '@/components/Selector/types';

export const Selector: FC<ISelector<string>> = ({
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
      <InputLabel
        id={`${label}-label`}
        sx={{
          top: '-1vh',
          '&.MuiInputLabel-shrink': {
            top: 0,
            transform: 'translate(3px, -9px) scale(0.7)',
          },
        }}
      >
        {label}
      </InputLabel>
      <Select
        className={styles.selector}
        labelId={`${label}-label`}
        id={label}
        value={value}
        label={label}
        onChange={handleChange}
      >
        {options.map((name) => (
          <MenuItem className={styles.menuItem} key={name} value={name}>
            {name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

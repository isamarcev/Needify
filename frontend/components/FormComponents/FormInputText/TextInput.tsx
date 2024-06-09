import { FC } from 'react';
import { TextField } from '@mui/material';
import { Controller } from 'react-hook-form';
import { IFormInputText } from '@/components/FormComponents/FormInputText/types';

export const FormInputText: FC<IFormInputText> = ({
  name,
  control,
  label,
  className,
  ...rest
}) => {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field: { onChange, value }, fieldState: { error } }) => (
        <TextField
          helperText={error ? error.message : null}
          size="small"
          error={!!error}
          onChange={onChange}
          value={value}
          fullWidth
          label={label}
          variant="outlined"
          className={className}
          {...rest}
        />
      )}
    />
  );
};

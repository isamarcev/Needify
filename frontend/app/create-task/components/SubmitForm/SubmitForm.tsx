import { useWatch } from 'react-hook-form-mui';
import { Alert, Button, Stack } from '@mui/material';

export const SubComponent = () => {
  const fields = useWatch();

  const isDisabled = Object.entries(fields)
    .filter(([key, _]) => key !== 'images')
    .some(([_, value]) => !value);

  return (
    <>
      <Stack spacing={3} marginTop={2}>
        <Button
          type="submit"
          color="primary"
          variant="contained"
          disabled={isDisabled}
        >
          Submit
        </Button>
        <Alert variant="outlined" severity="info">
          You have to fill out the required fields before the Button activates.
        </Alert>
      </Stack>
    </>
  );
};

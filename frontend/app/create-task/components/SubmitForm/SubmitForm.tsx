import { useWatch } from 'react-hook-form-mui';
import { Alert, Button, Stack } from '@mui/material';

export const SubComponent = () => {
  const fields = useWatch();

  return (
    <>
      <Stack spacing={3} marginTop={2}>
        <Button
          type="submit"
          color="primary"
          variant="contained"
          disabled={!fields.title}
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

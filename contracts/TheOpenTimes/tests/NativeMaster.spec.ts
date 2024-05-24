import { Blockchain, SandboxContract, TreasuryContract } from '@ton/sandbox';
import { toNano } from '@ton/core';
import { NativeMaster } from '../wrappers/NativeMaster';
import '@ton/test-utils';

describe('NativeMaster', () => {
    let blockchain: Blockchain;
    let deployer: SandboxContract<TreasuryContract>;
    let nativeMaster: SandboxContract<NativeMaster>;

    beforeEach(async () => {
        blockchain = await Blockchain.create();

        nativeMaster = blockchain.openContract(await NativeMaster.fromInit());

        deployer = await blockchain.treasury('deployer');

        const deployResult = await nativeMaster.send(
            deployer.getSender(),
            {
                value: toNano('0.05'),
            },
            {
                $$type: 'Deploy',
                queryId: 0n,
            }
        );

        expect(deployResult.transactions).toHaveTransaction({
            from: deployer.address,
            to: nativeMaster.address,
            deploy: true,
            success: true,
        });
    });

    it('should deploy', async () => {
        // the check is done inside beforeEach
        // blockchain and nativeMaster are ready to use
    });
});

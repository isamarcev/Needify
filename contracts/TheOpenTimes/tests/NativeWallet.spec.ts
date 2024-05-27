import { Blockchain, SandboxContract, TreasuryContract } from '@ton/sandbox';
import { toNano } from '@ton/core';
import { NativeWallet } from '../wrappers/NativeWallet';
import '@ton/test-utils';

describe('NativeWallet', () => {
    let blockchain: Blockchain;
    let deployer: SandboxContract<TreasuryContract>;
    let nativeWallet: SandboxContract<NativeWallet>;

    beforeEach(async () => {
        blockchain = await Blockchain.create();

        // nativeWallet = blockchain.openContract(await NativeWallet.fromInit());

        // deployer = await blockchain.treasury('deployer');

        // const deployResult = await nativeWallet.send(
        //     deployer.getSender(),
        //     {
        //         value: toNano('0.05'),
        //     },
        //     {
        //         $$type: 'Deploy',
        //         queryId: 0n,
        //     }
        // );

        // expect(deployResult.transactions).toHaveTransaction({
        //     from: deployer.address,
        //     to: nativeWallet.address,
        //     deploy: true,
        //     success: true,
        // });
    });

    it('should deploy', async () => {
        // the check is done inside beforeEach
        // blockchain and nativeWallet are ready to use
    });
});

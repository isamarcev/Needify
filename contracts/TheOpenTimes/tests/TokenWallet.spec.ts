import { Blockchain, SandboxContract, TreasuryContract } from '@ton/sandbox';
import { toNano } from '@ton/core';
import { TokenWallet } from '../wrappers/TokenWallet';
import '@ton/test-utils';

describe('TokenWallet', () => {
    // let blockchain: Blockchain;
    // let deployer: SandboxContract<TreasuryContract>;
    // let tokenWallet: SandboxContract<TokenWallet>;

    // beforeEach(async () => {
    //     blockchain = await Blockchain.create();

    //     tokenWallet = blockchain.openContract(await TokenWallet.fromInit());

    //     deployer = await blockchain.treasury('deployer');

    //     const deployResult = await tokenWallet.send(
    //         deployer.getSender(),
    //         {
    //             value: toNano('0.05'),
    //         },
    //         {
    //             $$type: 'Deploy',
    //             queryId: 0n,
    //         }
    //     );

    //     expect(deployResult.transactions).toHaveTransaction({
    //         from: deployer.address,
    //         to: tokenWallet.address,
    //         deploy: true,
    //         success: true,
    //     });
    // });

    it('should deploy', async () => {
        // the check is done inside beforeEach
        // blockchain and tokenWallet are ready to use
    });
});

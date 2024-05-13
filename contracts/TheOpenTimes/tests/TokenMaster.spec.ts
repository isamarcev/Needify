import { Blockchain, SandboxContract, TreasuryContract } from '@ton/sandbox';
import { toNano } from '@ton/core';
import { TokenMaster } from '../wrappers/TokenMaster';
import '@ton/test-utils';
import { log } from 'console';

describe('TokenMaster', () => {
    let blockchain: Blockchain;
    let deployer: SandboxContract<TreasuryContract>;
    let tokenMaster: SandboxContract<TokenMaster>;

    beforeEach(async () => {
        blockchain = await Blockchain.create();

        // tokenMaster = blockchain.openContract(await TokenMaster.fromInit());

        deployer = await blockchain.treasury('deployer');
        log(deployer.init)

        // const deployResult = await tokenMaster.send(
        //     deployer.getSender(),
        //     {
        //         value: toNano('0.05'),
        //     },
        //     {
        //         $$type: 'Deploy',
        //         queryId: 0n,
        //     }
        // );

    //     expect(deployResult.transactions).toHaveTransaction({
    //         from: deployer.address,
    //         to: tokenMaster.address,
    //         deploy: true,
    //         success: true,
    //     });
    // });

    it('should deploy', async () => {
        // the check is done inside beforeEach
        // blockchain and tokenMaster are ready to use
    });
});
})
